# CDN Links for NEXUS Hybrid Packages

## Using GitHub CDN (jsDelivr)

### NEXUS Icons Unified
```html
<!-- Via jsDelivr -->
<script src="https://cdn.jsdelivr.net/gh/Mattlk13/nexus-icons-unified@main/index.js"></script>

<!-- Via GitHub Pages (if enabled) -->
<script src="https://mattlk13.github.io/nexus-icons-unified/index.js"></script>
```

### NEXUS Design System
```html
<!-- CSS -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Mattlk13/nexus-design-system@main/index.css">

<!-- JS -->
<script src="https://cdn.jsdelivr.net/gh/Mattlk13/nexus-design-system@main/index.js"></script>
```

### NEXUS UI Components
```html
<script src="https://cdn.jsdelivr.net/gh/Mattlk13/nexus-ui-components@main/index.js"></script>
```

### NEXUS Mobile Kit
```html
<script src="https://cdn.jsdelivr.net/gh/Mattlk13/nexus-mobile-kit@main/index.js"></script>
```

---

## Using npm/yarn (Recommended)

```bash
npm install nexus-icons-unified nexus-design-system nexus-ui-components nexus-mobile-kit
```

---

## Cloudflare CDN Deployment (Optional)

To serve via Cloudflare Pages CDN:

1. Create a new Pages project: `nexus-hybrids-cdn`
2. Add all 4 repos as submodules
3. Build and deploy
4. Access via: `https://nexus-hybrids.pages.dev/icons-unified.js`

### Benefits:
- ⚡ Faster global delivery
- 🔒 DDoS protection
- 📊 Analytics
- 🌍 Edge caching

---

## NPM Publishing (Future)

To publish to npm registry:

```bash
cd /tmp/github-repos/nexus-icons-unified
npm publish

# Repeat for all 4 hybrids
```

Then users can:
```bash
npm install nexus-icons-unified
```

---

## Usage Examples

### Via CDN:
```html
<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Mattlk13/nexus-design-system@main/styles.css">
</head>
<body>
  <div id="app"></div>
  
  <script src="https://cdn.jsdelivr.net/gh/Mattlk13/nexus-icons-unified@main/index.js"></script>
  <script src="https://cdn.jsdelivr.net/gh/Mattlk13/nexus-ui-components@main/index.js"></script>
  
  <script>
    // Use components
    NexusIcons.render('nexus-spark', document.getElementById('app'));
  </script>
</body>
</html>
```

### Via npm:
```javascript
import { Icon } from 'nexus-icons-unified';
import { ProductCard, Button } from 'nexus-ui-components';
import { useResponsive } from 'nexus-mobile-kit';
import { typography, colors } from 'nexus-design-system';

function App() {
  const device = useResponsive();
  
  return (
    <div>
      <Icon name="nexus-spark" />
      <ProductCard title="Test" price={9.99} />
      <Button variant="primary">Click</Button>
    </div>
  );
}
```
