export interface Service {
  id: string;
  name: string;
  category: string;
  subcategory?: string;
  short_description: string;
  duration_minutes: number;
  base_price: number;
  skill_required: string;
  is_chemical: boolean;
  ar_preview_available: boolean;
  tags: string[];
  image_url?: string;
  is_active: boolean;
}
