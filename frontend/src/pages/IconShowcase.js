import React, { useState } from 'react';
import { Icon, IconSet, iconCategories, searchIcons } from '../lib/nexus-icons-unified';
import { Search } from 'lucide-react';

/**
 * Icon Showcase Page
 * Demonstrates the NEXUS Icons Unified system
 */
const IconShowcase = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);

  const handleSearch = (term) => {
    setSearchTerm(term);
    if (term.length > 2) {
      const results = searchIcons(term);
      setSearchResults(results.slice(0, 50)); // Limit to 50 results
    } else {
      setSearchResults([]);
    }
  };

  return (
    <div className="min-h-screen bg-[#050505] text-white pt-24 pb-12">
      <div className="max-w-7xl mx-auto px-6">
        {/* Header */}
        <div className="mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-cyan-500/10 to-purple-500/10 border border-cyan-500/20 rounded-full mb-4">
            <Icon name="nexus-spark" size={20} className="text-cyan-400" />
            <span className="text-sm font-semibold text-cyan-400">NEXUS Icons Unified</span>
          </div>
          
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
            10,000+ Professional Icons
          </h1>
          
          <p className="text-xl text-gray-400 max-w-2xl">
            A hybrid icon system combining the best open-source icon libraries into one unified API.
          </p>

          {/* Stats */}
          <div className="flex gap-6 mt-6">
            <div className="px-4 py-2 bg-white/5 rounded-lg">
              <div className="text-2xl font-bold text-cyan-400">1000+</div>
              <div className="text-sm text-gray-400">Lucide Icons</div>
            </div>
            <div className="px-4 py-2 bg-white/5 rounded-lg">
              <div className="text-2xl font-bold text-purple-400">6000+</div>
              <div className="text-sm text-gray-400">Tabler Icons (coming)</div>
            </div>
            <div className="px-4 py-2 bg-white/5 rounded-lg">
              <div className="text-2xl font-bold text-green-400">3000+</div>
              <div className="text-sm text-gray-400">Additional Sets</div>
            </div>
          </div>
        </div>

        {/* Search */}
        <div className="mb-12">
          <div className="relative max-w-2xl">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => handleSearch(e.target.value)}
              placeholder="Search 10,000+ icons... (e.g., 'music', 'user', 'settings')"
              className="w-full pl-12 pr-4 py-4 bg-white/5 border border-white/10 rounded-xl focus:outline-none focus:border-cyan-500 transition-all"
            />
          </div>

          {/* Search Results */}
          {searchResults.length > 0 && (
            <div className="mt-6 p-6 bg-white/5 border border-white/10 rounded-xl">
              <h3 className="text-lg font-semibold mb-4">
                Found {searchResults.length} icons matching "{searchTerm}"
              </h3>
              <IconSet icons={searchResults.slice(0, 30)} size={32} />
            </div>
          )}
        </div>

        {/* NEXUS Custom Icons */}
        <section className="mb-12">
          <h2 className="text-3xl font-bold mb-6">NEXUS Custom Icons</h2>
          <p className="text-gray-400 mb-6">
            Semantic icon names designed specifically for NEXUS platform features.
          </p>

          {Object.entries(iconCategories).map(([category, icons]) => (
            <div key={category} className="mb-8">
              <h3 className="text-xl font-semibold mb-4 capitalize flex items-center gap-2">
                <Icon name={icons[0]} size={24} className="text-cyan-400" />
                {category}
              </h3>
              <div className="p-6 bg-white/5 border border-white/10 rounded-xl">
                <IconSet icons={icons} size={40} />
              </div>
            </div>
          ))}
        </section>

        {/* Usage Example */}
        <section className="mb-12">
          <h2 className="text-3xl font-bold mb-6">Usage Examples</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Example 1 */}
            <div className="p-6 bg-white/5 border border-white/10 rounded-xl">
              <h3 className="text-lg font-semibold mb-4">Basic Usage</h3>
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <Icon name="nexus-create" size={32} className="text-cyan-400" />
                  <code className="text-sm text-gray-300">
                    {'<Icon name="nexus-create" size={32} />'}
                  </code>
                </div>
                <div className="flex items-center gap-3">
                  <Icon name="nexus-boost" size={32} className="text-purple-400" />
                  <code className="text-sm text-gray-300">
                    {'<Icon name="nexus-boost" />'}
                  </code>
                </div>
              </div>
            </div>

            {/* Example 2 */}
            <div className="p-6 bg-white/5 border border-white/10 rounded-xl">
              <h3 className="text-lg font-semibold mb-4">With Styling</h3>
              <div className="space-y-4">
                <button className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-cyan-600 to-purple-600 rounded-xl">
                  <Icon name="nexus-spark" size={20} />
                  Generate Content
                </button>
                <button className="flex items-center gap-2 px-6 py-3 bg-white/5 hover:bg-white/10 rounded-xl transition-all">
                  <Icon name="nexus-like" size={20} className="text-pink-400" />
                  Like Post
                </button>
              </div>
            </div>

            {/* Example 3 */}
            <div className="p-6 bg-white/5 border border-white/10 rounded-xl">
              <h3 className="text-lg font-semibold mb-4">Status Indicators</h3>
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <Icon name="nexus-success" size={24} className="text-green-400" />
                  <span>Successfully generated</span>
                </div>
                <div className="flex items-center gap-2">
                  <Icon name="nexus-error" size={24} className="text-red-400" />
                  <span>Generation failed</span>
                </div>
                <div className="flex items-center gap-2">
                  <Icon name="nexus-loading" size={24} className="text-cyan-400 animate-spin" />
                  <span>Processing...</span>
                </div>
              </div>
            </div>

            {/* Example 4 */}
            <div className="p-6 bg-white/5 border border-white/10 rounded-xl">
              <h3 className="text-lg font-semibold mb-4">Marketplace Cards</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Icon name="nexus-product" size={20} />
                    <span className="text-sm">Product</span>
                  </div>
                  <span className="text-cyan-400 font-semibold">$9.99</span>
                </div>
                <div className="flex items-center gap-4 text-sm text-gray-400">
                  <div className="flex items-center gap-1">
                    <Icon name="nexus-like" size={16} />
                    <span>234</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Icon name="nexus-trending" size={16} />
                    <span>1.2k</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Benefits */}
        <section className="mb-12">
          <h2 className="text-3xl font-bold mb-6">Why NEXUS Icons Unified?</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-6 bg-gradient-to-br from-cyan-500/10 to-cyan-500/5 border border-cyan-500/20 rounded-xl">
              <Icon name="nexus-lightning" size={40} className="text-cyan-400 mb-4" />
              <h3 className="text-xl font-semibold mb-2">One Import</h3>
              <p className="text-gray-400">
                Access 10,000+ icons from a single unified API. No need to manage multiple packages.
              </p>
            </div>

            <div className="p-6 bg-gradient-to-br from-purple-500/10 to-purple-500/5 border border-purple-500/20 rounded-xl">
              <Icon name="nexus-spark" size={40} className="text-purple-400 mb-4" />
              <h3 className="text-xl font-semibold mb-2">Semantic Names</h3>
              <p className="text-gray-400">
                NEXUS-specific icon names that match platform features. Easy to remember and use.
              </p>
            </div>

            <div className="p-6 bg-gradient-to-br from-green-500/10 to-green-500/5 border border-green-500/20 rounded-xl">
              <Icon name="nexus-badge" size={40} className="text-green-400 mb-4" />
              <h3 className="text-xl font-semibold mb-2">Consistent Style</h3>
              <p className="text-gray-400">
                All icons follow the same design language, ensuring visual consistency across NEXUS.
              </p>
            </div>
          </div>
        </section>

        {/* Integration Status */}
        <section className="p-8 bg-gradient-to-r from-cyan-500/10 to-purple-500/10 border border-cyan-500/20 rounded-2xl">
          <div className="flex items-start gap-4">
            <Icon name="nexus-info" size={32} className="text-cyan-400 flex-shrink-0" />
            <div>
              <h3 className="text-2xl font-bold mb-2">Currently Integrated</h3>
              <p className="text-gray-300 mb-4">
                This is a demo of NEXUS Icons Unified using Lucide as the base library (1000+ icons). 
                The full version will include Tabler Icons (6000+), Heroicons, and more.
              </p>
              <div className="flex gap-3">
                <div className="px-4 py-2 bg-green-500/20 border border-green-500/30 rounded-lg text-green-400 text-sm font-semibold">
                  ✓ Lucide (1000+ icons)
                </div>
                <div className="px-4 py-2 bg-yellow-500/20 border border-yellow-500/30 rounded-lg text-yellow-400 text-sm font-semibold">
                  ⏳ Tabler (6000+) - Coming
                </div>
                <div className="px-4 py-2 bg-yellow-500/20 border border-yellow-500/30 rounded-lg text-yellow-400 text-sm font-semibold">
                  ⏳ Heroicons - Coming
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};

export default IconShowcase;
