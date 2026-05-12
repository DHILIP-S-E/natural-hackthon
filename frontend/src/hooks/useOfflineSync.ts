import { useEffect, useState } from 'react'
import { enqueueWrite, startOnlineSyncListener, getPendingCount, QueuedWrite } from '../lib/offlineDb'
import api from '../config/api'

async function replayWrite(write: QueuedWrite): Promise<void> {
  await api.request({
    url: write.url,
    method: write.method,
    data: write.body,
    headers: write.headers,
  })
}

export function useOfflineSync() {
  const [isOnline, setIsOnline] = useState(navigator.onLine)
  const [pendingCount, setPendingCount] = useState(0)
  const [lastSync, setLastSync] = useState<Date | null>(null)

  useEffect(() => {
    const onOnline = () => setIsOnline(true)
    const onOffline = () => setIsOnline(false)
    window.addEventListener('online', onOnline)
    window.addEventListener('offline', onOffline)

    const stopSync = startOnlineSyncListener(replayWrite, (result) => {
      setLastSync(new Date())
      setPendingCount(prev => Math.max(0, prev - result.flushed))
    })

    getPendingCount().then(setPendingCount)

    return () => {
      window.removeEventListener('online', onOnline)
      window.removeEventListener('offline', onOffline)
      stopSync()
    }
  }, [])

  const queueWrite = async (
    url: string,
    method: QueuedWrite['method'],
    body: unknown,
    headers?: Record<string, string>,
  ) => {
    if (isOnline) {
      await api.request({ url, method, data: body, headers })
    } else {
      await enqueueWrite({ url, method, body, headers })
      setPendingCount(c => c + 1)
    }
  }

  return { isOnline, pendingCount, lastSync, queueWrite }
}
