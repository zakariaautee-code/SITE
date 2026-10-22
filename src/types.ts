export interface Listing {
  id: string;
  category: string;
  categoryName: string;
  city: string;
  slug: string;
  title: string;
  excerpt: string;
  price: number;
  priceLabel: string;
  priceCurrency: string;
  availability: 'InStock' | 'OutOfStock' | 'PreOrder' | string;
  rating?: number;
  reviewCount?: number;
  features?: string[];
  provider?: {
    name: string;
    type: string;
    telephone?: string;
    address?: string;
    url?: string;
  };
  seo?: {
    description?: string;
    keywords?: string;
  };
  updatedAt?: string;
}

export interface Category {
  slug: string;
  name: string;
  emoji: string;
}
