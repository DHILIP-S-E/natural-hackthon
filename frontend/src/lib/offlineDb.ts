/**
 * Offline-First PWA — Idea 24: IndexedDB write queue.
 *
 * When the network is unavailable, writes (booking creation, consultation
 * submit, session notes) are queued here and replayed via Background Sync
 * once connectivity returns.
 *
 * Structure:
 *   DB: aura_offline  v1
 *   Stores:
 *     - write_queue  (pending API calls to be replayed)
 *     - read_cache   (cached API responses for offline reads)
 */

const DB_NAME = 'aura_offline'
const DB_VERSION = 1

export interface QueuedWrite {
  id?: number
  url: string
  method: 'POST' | 'PUT' | 'PATCH' | 'DELETE'
  body: unknown
  headers?: Record<string, string>
  queued_at: string
  retry_count: number
}

export interface CachedRead {
  id?: number
  key: string        // cache key = URL + query string
  data: unknown
  cached_at: string
  ttl_ms: number
}

function openDb(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, DB_VERSION)
    req.onupgradeneeded = () => {
      const db = req.result
      if (!db.objectStoreNames.contains('write_queue')) {
        db.createObjectStore('write_queue', { keyPath: 'id', autoIncrement: true })
      }
      if (!db.objectStoreNames.contains('read_cache')) {
        const store = db.createObjectStore('read_cache', { keyPath: 'id', autoIncrement: true })
        store.createIndex('by_key', 'key', { unique: true })
      }
    }
    req.onsuccess = () => resolve(req.result)
    req.onerror = () => reject(req.error)
  })
}

// ── Write queue ──

export async function enqueueWrite(write: Omit<QueuedWrite, 'id' | 'queued_at' | 'retry_count'>): Promise<void> {
  const db = await openDb()
  await new Promise<void>((resolve, reject) => {
    const tx = db.transaction('write_queue', 'readwrite')
    tx.objectStore('write_queue').add({
      ...write,
      queued_at: new Date().toISOString(),
      retry_count: 0,
    })
    tx.oncomplete = () => resolve()
    tx.onerror = () => reject(tx.error)
  })
  // Request Background Sync if supported
  if ('serviceWorker' in navigator && 'SyncManager' in window) {
    const reg = await navigator.serviceWorker.ready
    await (reg as any).sync?.register('aura-write-queue')
  }
}

export async function getPendingWrites(): Promise<QueuedWrite[]> {
  const db = await openDb()
  return new Promise((resolve, reject) => {
    const tx = db.transaction('write_queue', 'readonly')
    const req = tx.objectStore('write_queue').getAll()
    req.onsuccess = () => resolve(req.result as QueuedWrite[])
    req.onerror = () => reject(req.error)
  })
}

export async function removeWrite(id: number): Promise<void> {
  const db = await openDb()
  await new Promise<void>((resolve, reject) => {
    const tx = db.transaction('write_queue', 'readwrite')
    tx.objectStore('write_queue').delete(id)
    tx.oncomplete = () => resolve()
    tx.onerror = () => reject(tx.error)
  })
}

export async function flushWriteQueue(
  fetcher: (write: QueuedWrite) => Promise<void>,
): Promise<{ flushed: number; failed: number }> {
  const pending = await getPendingWrites()
  let flushed = 0
  let failed = 0
  for (const write of pending) {
    try {
      await fetcher(write)
      await removeWrite(write.id!)
      flushed++
    } catch {
      failed++
    }
  }
  return { flushed, failed }
}

// ── Read cache ──

export async function cacheRead(key: string, data: unknown, ttlMs = 5 * 60 * 1000): Promise<void> {
  const db = await openDb()
  await new Promise<void>((resolve, reject) => {
    const tx = db.transaction('read_cache', 'readwrite')
    const store = tx.objectStore('read_cache')
    // Delete old entry with same key first
    const idx = store.index('by_key')
    const getReq = idx.get(key)
    getReq.onsuccess = () => {
      if (getReq.result) store.delete(getReq.result.id)
      store.add({ key, data, cached_at: new Date().toISOString(), ttl_ms: ttlMs })
    }
    tx.oncomplete = () => resolve()
    tx.onerror = () => reject(tx.error)
  })
}

export async function getCachedRead(key: string): Promise<unknown | null> {
  const db = await openDb()
  return new Promise((resolve, reject) => {
    const tx = db.transaction('read_cache', 'readonly')
    const req = tx.objectStore('read_cache').index('by_key').get(key)
    req.onsuccess = () => {
      const entry = req.result as CachedRead | undefined
      if (!entry) return resolve(null)
      const age = Date.now() - new Date(entry.cached_at).getTime()
      if (age > entry.ttl_ms) return resolve(null)
      resolve(entry.data)
    }
    req.onerror = () => reject(req.error)
  })
}

// ── Online/offline sync ──

export function startOnlineSyncListener(
  fetcher: (write: QueuedWrite) => Promise<void>,
  onSync?: (result: { flushed: number; failed: number }) => void,
): () => void {
  const handler = async () => {
    if (navigator.onLine) {
      const result = await flushWriteQueue(fetcher)
      if (result.flushed > 0) onSync?.(result)
    }
  }
  window.addEventListener('online', handler)
  return () => window.removeEventListener('online', handler)
}

export function getPendingCount(): Promise<number> {
  return getPendingWrites().then(w => w.length)
}
