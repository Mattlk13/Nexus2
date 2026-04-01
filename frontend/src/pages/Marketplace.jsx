import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Search, ShoppingBag, Star, TrendingUp, DollarSign } from 'lucide-react';

const Marketplace = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [category, setCategory] = useState('all');

  const categories = ['All', 'Videos', 'Images', 'Audio', 'E-books', 'Code'];
  
  const featuredItems = [
    {
      id: 1,
      title: 'AI-Generated Sunset Video',
      creator: 'John Doe',
      price: 29.99,
      type: 'video',
      rating: 4.8,
      sales: 152
    },
    {
      id: 2,
      title: 'Abstract Art Collection',
      creator: 'Jane Smith',
      price: 19.99,
      type: 'image',
      rating: 4.9,
      sales: 284
    },
    {
      id: 3,
      title: 'Ambient Music Pack',
      creator: 'Audio Pro',
      price: 39.99,
      type: 'audio',
      rating: 4.7,
      sales: 98
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent flex items-center">
            <ShoppingBag className="h-8 w-8 mr-3 text-green-600" />
            Marketplace
          </h1>
          <p className="text-gray-600 mt-2">Buy and sell AI-generated content</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        
        {/* Search & Filters */}
        <Card className="mb-6">
          <CardContent className="pt-6">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                <Input
                  placeholder="Search marketplace..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
              <div className="flex gap-2 flex-wrap">
                {categories.map(cat => (
                  <Button
                    key={cat}
                    variant={category === cat.toLowerCase() ? 'default' : 'outline'}
                    onClick={() => setCategory(cat.toLowerCase())}
                    size="sm"
                  >
                    {cat}
                  </Button>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card>
            <CardContent className="pt-6 text-center">
              <TrendingUp className="h-8 w-8 mx-auto mb-2 text-green-600" />
              <p className="text-2xl font-bold">1,234</p>
              <p className="text-sm text-gray-600">Total Items</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6 text-center">
              <ShoppingBag className="h-8 w-8 mx-auto mb-2 text-blue-600" />
              <p className="text-2xl font-bold">5,678</p>
              <p className="text-sm text-gray-600">Sales</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6 text-center">
              <DollarSign className="h-8 w-8 mx-auto mb-2 text-purple-600" />
              <p className="text-2xl font-bold">$234K</p>
              <p className="text-sm text-gray-600">Revenue</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6 text-center">
              <Star className="h-8 w-8 mx-auto mb-2 text-yellow-600" />
              <p className="text-2xl font-bold">4.8</p>
              <p className="text-sm text-gray-600">Avg Rating</p>
            </CardContent>
          </Card>
        </div>

        {/* Featured Items */}
        <h2 className="text-2xl font-bold mb-4">Featured Items</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {featuredItems.map(item => (
            <Card key={item.id} className="hover:shadow-lg transition-shadow">
              <div className="h-48 bg-gradient-to-br from-purple-400 to-pink-400 rounded-t-lg" />
              <CardHeader>
                <CardTitle className="text-lg">{item.title}</CardTitle>
                <p className="text-sm text-gray-600">by {item.creator}</p>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between mb-4">
                  <span className="text-2xl font-bold text-green-600">
                    ${item.price}
                  </span>
                  <div className="flex items-center">
                    <Star className="h-4 w-4 text-yellow-500 fill-current" />
                    <span className="ml-1 text-sm">{item.rating}</span>
                  </div>
                </div>
                <p className="text-sm text-gray-600 mb-4">{item.sales} sales</p>
                <Button className="w-full">Add to Cart</Button>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Become a Vendor CTA */}
        <Card className="mt-8 bg-gradient-to-r from-blue-500 to-purple-600 text-white">
          <CardContent className="py-12 text-center">
            <h2 className="text-3xl font-bold mb-4">Become a Vendor</h2>
            <p className="text-lg mb-6 opacity-90">
              Sell your AI-generated content and earn money
            </p>
            <Button size="lg" variant="secondary">
              Start Selling
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Marketplace;
