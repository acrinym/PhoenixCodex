#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

class MHTMLBundler {
    constructor() {
        this.baseDir = process.cwd();
        this.distDir = path.join(this.baseDir, 'dist');
        this.outputFile = path.join(this.baseDir, 'phoenix-codex.mhtml');
    }
    
    async build() {
        console.log('🚀 Building Phoenix Codex...');
        
        try {
            // Clean dist directory
            if (fs.existsSync(this.distDir)) {
                fs.rmSync(this.distDir, { recursive: true, force: true });
            }
            
            // Install dependencies if needed
            if (!fs.existsSync('node_modules')) {
                console.log('📦 Installing dependencies...');
                execSync('npm install', { stdio: 'inherit' });
            }
            
            // Build the application
            console.log('🔨 Building application...');
            execSync('npm run build', { stdio: 'inherit' });
            
            // Create MHTML bundle
            console.log('📦 Creating MHTML bundle...');
            await this.createMHTMLBundle();
            
            console.log('✅ Phoenix Codex MHTML bundle created successfully!');
            console.log(`📁 Output: ${this.outputFile}`);
            
        } catch (error) {
            console.error('❌ Error building Phoenix Codex:', error);
            process.exit(1);
        }
    }
    
    async createMHTMLBundle() {
        const htmlContent = await this.readHTMLFile();
        const cssContent = await this.readCSSFiles();
        const jsContent = await this.readJSFiles();
        
        const mhtmlContent = this.generateMHTML(htmlContent, cssContent, jsContent);
        
        fs.writeFileSync(this.outputFile, mhtmlContent);
    }
    
    async readHTMLFile() {
        const htmlPath = path.join(this.distDir, 'index.html');
        if (!fs.existsSync(htmlPath)) {
            throw new Error('Built HTML file not found. Run npm run build first.');
        }
        
        let html = fs.readFileSync(htmlPath, 'utf8');
        
        // Remove script and link tags as we'll inline everything
        html = html.replace(/<script[^>]*src="[^"]*"[^>]*><\/script>/g, '');
        html = html.replace(/<link[^>]*href="[^"]*"[^>]*>/g, '');
        
        return html;
    }
    
    async readCSSFiles() {
        const cssFiles = [];
        const assetsDir = path.join(this.distDir, 'assets');
        
        if (fs.existsSync(assetsDir)) {
            const files = fs.readdirSync(assetsDir);
            for (const file of files) {
                if (file.endsWith('.css')) {
                    const cssPath = path.join(assetsDir, file);
                    const css = fs.readFileSync(cssPath, 'utf8');
                    cssFiles.push(css);
                }
            }
        }
        
        return cssFiles.join('\n');
    }
    
    async readJSFiles() {
        const jsFiles = [];
        const assetsDir = path.join(this.distDir, 'assets');
        
        if (fs.existsSync(assetsDir)) {
            const files = fs.readdirSync(assetsDir);
            for (const file of files) {
                if (file.endsWith('.js')) {
                    const jsPath = path.join(assetsDir, file);
                    const js = fs.readFileSync(jsPath, 'utf8');
                    jsFiles.push(js);
                }
            }
        }
        
        return jsFiles.join('\n');
    }
    
    generateMHTML(html, css, js) {
        const boundary = '----=_NextPart_000_0000_01C12345.6789ABCD';
        const date = new Date().toUTCString();
        
        // Insert the CSS and JavaScript into the HTML
        const cssStyle = `<style>\n${css}\n</style>`;
        const jsScript = `<script type="module">${js}</script>`;
        
        // Insert CSS in the head
        html = html.replace('</head>', `${cssStyle}\n</head>`);
        
        // Insert JavaScript before closing body tag
        html = html.replace('</body>', `${jsScript}\n</body>`);
        
        let mhtml = `From: <saved-by-phoenix-codex@localhost>
Subject: Phoenix Codex - Interactive Visualization
Date: ${date}
MIME-Version: 1.0
Content-Type: multipart/related;
\ttype="text/html";
\tboundary="${boundary}"

This is a multi-part message in MIME format.

--${boundary}
Content-Type: text/html;
\tcharset="UTF-8"
Content-Transfer-Encoding: 7bit

${html}

--${boundary}--
`;

        return mhtml;
    }
}

// Run the bundler
const bundler = new MHTMLBundler();
bundler.build().catch(console.error); 