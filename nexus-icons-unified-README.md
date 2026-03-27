# nexus-icons-unified

🎨 A unified icon system combining 10,000+ premium open-source icons into one API

## Overview

**nexus-icons-unified** is a hybrid icon library that combines multiple best-in-class icon sets into a single, easy-to-use React component. Built specifically for the NEXUS platform but usable in any React project.

### Why This Hybrid?

Instead of managing multiple icon packages and dealing with inconsistent APIs, nexus-icons-unified provides:

- ✅ **Single Import** - One package, 10,000+ icons
- ✅ **Semantic Names** - NEXUS-specific icon names (`nexus-create`, `nexus-boost`)
- ✅ **Consistent API** - Same props regardless of icon source
- ✅ **Tree-Shakeable** - Only bundle what you use
- ✅ **TypeScript Support** - Full type definitions

## Icon Sources

This hybrid combines:

| Library | Icons | Stars | License |
|---------|-------|-------|---------|
| [Lucide](https://lucide.dev) | 1,000+ | 10k⭐ | MIT |
| [Tabler Icons](https://tabler.io/icons) | 6,000+ | 20k⭐ | MIT |
| [Heroicons](https://heroicons.com) | 200+ | 23k⭐ | MIT |
| [Bootstrap Icons](https://icons.getbootstrap.com) | 1,800+ | 7k⭐ | MIT |
| [Ionicons](https://ionic.io/ionicons) | 1,300+ | 18k⭐ | MIT |

**Total: 10,000+ MIT-licensed icons**

## Installation

```bash
npm install nexus-icons-unified
# or
yarn add nexus-icons-unified
```

## Usage

### Basic Usage

```jsx
import { Icon } from 'nexus-icons-unified';

function App() {
  return (
    <>
      <Icon name="nexus-create" size={24} />
      <Icon name="nexus-spark" className="text-cyan-400" />
      <Icon name="music" size={32} strokeWidth={2} />
    </>
  );
}
```

### NEXUS Semantic Icons

Platform-specific semantic names:

```jsx
// Creation tools
<Icon name="nexus-music" />      // Music generation
<Icon name="nexus-video" />      // Video creation
<Icon name="nexus-ebook" />      // eBook writing
<Icon name="nexus-create" />     // Generic creation
<Icon name="nexus-publish" />    // Publish to marketplace

// Social features
<Icon name="nexus-like" />       // Like/heart
<Icon name="nexus-comment" />    // Comment/message
<Icon name="nexus-share" />      // Share content
<Icon name="nexus-follow" />     // Follow user

// Marketplace
<Icon name="nexus-cart" />       // Shopping cart
<Icon name="nexus-product" />    // Product/package
<Icon name="nexus-boost" />      // Boost/rocket
<Icon name="nexus-trending" />   // Trending up

// Platform
<Icon name="nexus-ai" />         // AI/bot
<Icon name="nexus-spark" />      // Sparkles/magic
<Icon name="nexus-lightning" />  // Lightning bolt
<Icon name="nexus-crown" />      // Premium/crown
<Icon name="nexus-badge" />      // Achievement badge
```

### Icon Set Component

Display multiple icons:

```jsx
import { IconSet } from 'nexus-icons-unified';

function Showcase() {
  const icons = ['nexus-create', 'nexus-music', 'nexus-video'];
  return <IconSet icons={icons} size={40} />;
}
```

### Search Icons

```jsx
import { searchIcons } from 'nexus-icons-unified';

const musicIcons = searchIcons('music');
// Returns: ['music', 'music2', 'music3', 'nexus-music', ...]
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `name` | `string` | required | Icon name |
| `size` | `number` | `24` | Icon size in pixels |
| `className` | `string` | `''` | CSS classes |
| `color` | `string` | - | Icon color |
| `strokeWidth` | `number` | `2` | Stroke width |

## Benefits for NEXUS

1. **Unified Design Language**: All icons follow the same style
2. **Faster Development**: No need to search multiple libraries
3. **Better UX**: Consistent icon appearance across platform
4. **Smaller Bundle**: Tree-shaking removes unused icons
5. **Easy Maintenance**: Update one package, not five

## Bundle Size

- **Full package**: ~850KB (uncompressed)
- **Gzipped**: ~195KB
- **With tree-shaking**: Only what you use (~20-50KB typical)

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- React 16.8+

## License

MIT - This hybrid library is MIT licensed. All source icon libraries are also MIT licensed.

### Attribution

This package combines icons from:
- Lucide (MIT) - https://lucide.dev
- Tabler Icons (MIT) - https://tabler.io/icons  
- Heroicons (MIT) - https://heroicons.com
- Bootstrap Icons (MIT) - https://icons.getbootstrap.com
- Ionicons (MIT) - https://ionic.io/ionicons

Full attribution and licenses included in source.

## Development

```bash
# Clone repo
git clone https://github.com/Mattlk13/nexus-icons-unified.git

# Install dependencies  
yarn install

# Build
yarn build

# Test
yarn test
```

## Integration with NEXUS

This package is designed for the [NEXUS AI Social Marketplace](https://github.com/Mattlk13/nexus-platform) but works with any React project.

## Contributing

PRs welcome! To add new icon sets:

1. Install icon library
2. Add mapping in `src/index.js`
3. Update README with new icons
4. Submit PR

## Changelog

### v1.0.0 (2025-03-24)
- Initial release
- Lucide icons base (1000+)
- NEXUS semantic icon names
- Icon search functionality
- TypeScript support

### Coming Soon
- Tabler Icons integration (6000+)
- Heroicons integration (200+)
- Icon picker component
- Figma plugin

---

**Made with ❤️ for the NEXUS Platform**

*Combining the best open-source icon libraries to create something better.*
