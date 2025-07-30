# Phoenix Codex - Interactive Web Application

A modern, interactive web application for visualizing and analyzing AmandaMap and Phoenix Codex data with Three.js 3D visualizations, timeline analysis, and advanced search capabilities.

## 🚀 Features

### 📊 Dashboard
- **Data Overview**: Real-time statistics including total entries, unique sources, date ranges, and content analysis
- **Interactive Charts**: Content type distribution, timeline activity, and tag cloud visualization
- **Responsive Design**: Modern UI with Phoenix Fire theme and multiple color schemes

### 🎨 3D Visualizations
- **Network Graphs**: Interactive 3D network visualization of data relationships
- **3D Timeline**: Chronological data visualization in three-dimensional space
- **Content Clusters**: Tag-based clustering with Three.js particle systems
- **Relationship Maps**: Source-to-source relationship visualization
- **Real-time Controls**: Camera controls, animation speed, and color scheme selection

### 📅 Timeline Analysis
- **Interactive Timeline**: 2D timeline with filtering and date range selection
- **Type Filtering**: Filter by conversation, thought, memory, or event types
- **Date Range Picker**: Custom date range selection for focused analysis
- **Smooth Animations**: Animated timeline items with intersection observer

### 🔍 Advanced Search
- **Semantic Search**: Intelligent search with keyword expansion
- **Multi-field Search**: Search across content, source, type, and tags
- **Search Options**: Case-sensitive, semantic, and tag-inclusive search modes
- **Result Highlighting**: Highlighted search terms in results
- **Pagination**: Navigate through large result sets

### ⚙️ Settings & Data Management
- **File Upload**: Support for JSON and CSV data files
- **Data Export**: Export data as JSON or CSV formats
- **Theme Selection**: Phoenix Fire, Ocean Blue, Forest Green, and Sunset Orange themes
- **Performance Modes**: Balanced, High Quality, and High Performance options
- **Animation Controls**: Enable/disable animations for better performance

## 🛠️ Technology Stack

- **Frontend**: Modern HTML5, CSS3, and ES6+ JavaScript
- **3D Graphics**: Three.js for interactive 3D visualizations
- **Build Tool**: Vite for fast development and optimized builds
- **Styling**: CSS Custom Properties with responsive design
- **Icons**: Font Awesome for consistent iconography
- **Fonts**: Inter font family for modern typography

## 📦 Installation & Setup

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn package manager

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd PhoenixCodex
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

4. **Build for production**
   ```bash
   npm run build
   ```

5. **Create MHTML bundle**
   ```bash
   npm run bundle
   ```

## 🎯 Usage

### Development Mode
```bash
npm run dev
```
Opens the application at `http://localhost:3000` with hot module replacement.

### Production Build
```bash
npm run build
```
Creates optimized production files in the `dist` directory.

### MHTML Bundle
```bash
npm run bundle
```
Creates a single `phoenix-codex.mhtml` file that can be opened in any browser.

### Preview Production Build
```bash
npm run preview
```
Serves the production build locally for testing.

## 📁 Project Structure

```
PhoenixCodex/
├── index.html                 # Main HTML file
├── package.json              # Dependencies and scripts
├── vite.config.js           # Vite configuration
├── styles/                  # CSS stylesheets
│   ├── main.css            # Main styles and theme variables
│   ├── components.css      # Component-specific styles
│   └── visualization.css   # 3D visualization styles
├── js/                     # JavaScript modules
│   ├── main.js            # Main application logic
│   ├── visualization.js   # Three.js 3D visualizations
│   ├── timeline.js        # Timeline analysis module
│   ├── search.js          # Search functionality
│   ├── settings.js        # Settings and data management
│   └── utils.js           # Utility functions and classes
├── scripts/               # Build scripts
│   └── bundle-mhtml.js   # MHTML bundler
├── data/                  # Sample data files
│   └── sample_visualization_data.json
└── dist/                  # Built files (generated)
```

## 🎨 Themes

The application supports four beautiful themes:

### Phoenix Fire (Default)
- Primary: `#ff6b35` (Orange)
- Secondary: `#f7931e` (Golden Orange)
- Accent: `#ffd23f` (Yellow)
- Dark: `#2c1810` (Dark Brown)

### Ocean Blue
- Primary: `#0066cc` (Blue)
- Secondary: `#0099ff` (Light Blue)
- Accent: `#00ccff` (Cyan)
- Dark: `#003366` (Dark Blue)

### Forest Green
- Primary: `#2d5a27` (Dark Green)
- Secondary: `#4a7c59` (Medium Green)
- Accent: `#6b8e23` (Olive)
- Dark: `#1a3d1a` (Very Dark Green)

### Sunset Orange
- Primary: `#ff8c42` (Orange)
- Secondary: `#ff6b6b` (Coral)
- Accent: `#ffd93d` (Yellow)
- Dark: `#8b4513` (Saddle Brown)

## 📊 Data Format

The application expects data in the following JSON format:

```json
[
  {
    "date": "2024-01-15T00:00:00",
    "source": "Amanda",
    "type": "conversation",
    "content": "Sample conversation content...",
    "tags": ["love", "family", "important"]
  }
]
```

### Required Fields
- `date`: ISO 8601 date string
- `source`: String identifying the data source
- `type`: One of "conversation", "thought", "memory", or "event"
- `content`: The main text content
- `tags`: Array of string tags (optional)

## 🔧 Configuration

### Performance Modes
- **Balanced**: Default mode with good performance and quality
- **High Quality**: Maximum visual quality with higher resource usage
- **High Performance**: Optimized for performance on lower-end devices

### Animation Settings
- Enable/disable animations globally
- Adjust animation speed in 3D visualizations
- Smooth transitions between data states

## 🌐 Browser Support

- **Modern Browsers**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **WebGL Support**: Required for 3D visualizations
- **ES6+ Support**: Required for modern JavaScript features

## 🚀 Deployment

### Static Hosting
The built application can be deployed to any static hosting service:

1. Run `npm run build`
2. Upload the `dist` directory to your hosting service
3. Configure your server to serve `index.html` for all routes

### MHTML Distribution
For easy sharing and offline use:

1. Run `npm run bundle`
2. Share the generated `phoenix-codex.mhtml` file
3. Open in any modern browser

## 🔍 Troubleshooting

### Common Issues

**3D Visualizations not working**
- Ensure WebGL is enabled in your browser
- Check browser console for Three.js errors
- Try switching to "High Performance" mode

**Data not loading**
- Verify JSON format matches expected schema
- Check browser console for parsing errors
- Ensure file encoding is UTF-8

**Performance issues**
- Switch to "High Performance" mode
- Disable animations in settings
- Reduce data set size for testing

### Development Tips

**Adding new visualizations**
1. Extend the `VisualizationManager` class
2. Add new visualization type to the HTML select
3. Implement the visualization logic in `visualization.js`

**Custom themes**
1. Add theme colors to CSS custom properties
2. Update the theme selector in HTML
3. Add theme logic to the main application

## 📈 Performance Optimization

- **Lazy Loading**: Components load only when needed
- **Debounced Search**: Prevents excessive API calls
- **Virtual Scrolling**: Efficient rendering of large datasets
- **WebGL Optimization**: Efficient Three.js rendering
- **CSS Optimization**: Minimal repaints and reflows

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Three.js**: 3D graphics library
- **Vite**: Build tool and development server
- **Font Awesome**: Icon library
- **Inter Font**: Typography

---

**Phoenix Codex** - Transforming data visualization with modern web technologies and interactive 3D experiences. 