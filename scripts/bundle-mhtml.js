#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');
const { URL } = require('url');

/**
 * Enhanced MHTML Bundler for Phoenix Codex
 * Creates truly self-contained MHTML files with all dependencies embedded
 */

class MHTMLBundler {
    constructor() {
        this.boundary = 'boundary-' + Math.random().toString(36).substr(2, 9);
        this.baseDir = process.cwd();
        this.externalResources = new Map();
        this.userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36';
    }

    /**
     * Fetch external resource
     */
    async fetchExternalResource(url) {
        if (this.externalResources.has(url)) {
            return this.externalResources.get(url);
        }

        console.log(`Fetching external resource: ${url}`);
        
        return new Promise((resolve, reject) => {
            const urlObj = new URL(url);
            const client = urlObj.protocol === 'https:' ? https : http;
            
            const options = {
                hostname: urlObj.hostname,
                port: urlObj.port,
                path: urlObj.pathname + urlObj.search,
                headers: {
                    'User-Agent': this.userAgent,
                    'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive'
                }
            };

            const req = client.request(options, (res) => {
                let data = Buffer.alloc(0);
                
                res.on('data', (chunk) => {
                    data = Buffer.concat([data, chunk]);
                });

                res.on('end', () => {
                    const result = {
                        data: data,
                        contentType: res.headers['content-type'] || this.getContentTypeFromUrl(url),
                        encoding: 'base64'
                    };
                    
                    this.externalResources.set(url, result);
                    resolve(result);
                });
            });

            req.on('error', (err) => {
                console.warn(`Failed to fetch ${url}: ${err.message}`);
                resolve(null);
            });

            req.setTimeout(10000, () => {
                req.abort();
                console.warn(`Timeout fetching ${url}`);
                resolve(null);
            });

            req.end();
        });
    }

    /**
     * Get content type from URL
     */
    getContentTypeFromUrl(url) {
        const ext = path.extname(new URL(url).pathname).toLowerCase();
        const contentTypes = {
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.woff': 'font/woff',
            '.woff2': 'font/woff2',
            '.ttf': 'font/ttf',
            '.otf': 'font/otf',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml'
        };
        return contentTypes[ext] || 'application/octet-stream';
    }

    /**
     * Read and encode file content for MHTML
     */
    encodeFile(filePath, contentType) {
        try {
            const content = fs.readFileSync(filePath);
            const base64Content = content.toString('base64');
            
            return {
                location: filePath,
                contentType: contentType || this.getContentType(filePath),
                content: base64Content,
                encoding: 'base64'
            };
        } catch (error) {
            console.warn(`Warning: Could not read file ${filePath}: ${error.message}`);
            return null;
        }
    }

    /**
     * Get MIME content type based on file extension
     */
    getContentType(filePath) {
        const ext = path.extname(filePath).toLowerCase();
        const contentTypes = {
            '.html': 'text/html',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
            '.woff': 'font/woff',
            '.woff2': 'font/woff2',
            '.ttf': 'font/ttf',
            '.otf': 'font/otf',
            '.json': 'application/json'
        };
        return contentTypes[ext] || 'application/octet-stream';
    }

    /**
     * Extract referenced files from HTML content
     */
    extractReferences(htmlContent, htmlDir) {
        const references = {
            local: new Set(),
            external: new Set()
        };
        
        // Extract CSS files
        const cssMatches = htmlContent.match(/(?:href|src)=["']([^"']*\.css)[^"']*["']/gi);
        if (cssMatches) {
            cssMatches.forEach(match => {
                const url = match.match(/["']([^"']*)["']/)[1];
                if (url.startsWith('http') || url.startsWith('//')) {
                    const fullUrl = url.startsWith('//') ? 'https:' + url : url;
                    references.external.add(fullUrl);
                } else {
                    references.local.add(path.resolve(htmlDir, url));
                }
            });
        }

        // Extract JavaScript files
        const jsMatches = htmlContent.match(/src=["']([^"']*\.js)[^"']*["']/gi);
        if (jsMatches) {
            jsMatches.forEach(match => {
                const url = match.match(/["']([^"']*)["']/)[1];
                if (url.startsWith('http') || url.startsWith('//')) {
                    const fullUrl = url.startsWith('//') ? 'https:' + url : url;
                    references.external.add(fullUrl);
                } else {
                    references.local.add(path.resolve(htmlDir, url));
                }
            });
        }

        // Extract image files
        const imgMatches = htmlContent.match(/(?:src|href)=["']([^"']*\.(png|jpg|jpeg|gif|svg))[^"']*["']/gi);
        if (imgMatches) {
            imgMatches.forEach(match => {
                const url = match.match(/["']([^"']*)["']/)[1];
                if (url.startsWith('http') || url.startsWith('//')) {
                    const fullUrl = url.startsWith('//') ? 'https:' + url : url;
                    references.external.add(fullUrl);
                } else {
                    references.local.add(path.resolve(htmlDir, url));
                }
            });
        }

        // Extract Google Fonts and other external stylesheets
        const linkMatches = htmlContent.match(/<link[^>]*href=["']([^"']*\.css|[^"']*fonts\.googleapis\.com[^"']*)["'][^>]*>/gi);
        if (linkMatches) {
            linkMatches.forEach(match => {
                const url = match.match(/href=["']([^"']*)["']/)[1];
                if (url.startsWith('http') || url.startsWith('//')) {
                    const fullUrl = url.startsWith('//') ? 'https:' + url : url;
                    references.external.add(fullUrl);
                }
            });
        }

        return references;
    }

    /**
     * Process CSS content to extract font and image references
     */
    async processCSSContent(cssContent, baseUrl) {
        const references = new Set();
        
        // Extract font files from CSS
        const fontMatches = cssContent.match(/url\(["']?([^"')]*\.(woff2?|ttf|otf|eot))["']?\)/gi);
        if (fontMatches) {
            for (const match of fontMatches) {
                const url = match.match(/url\(["']?([^"')]*)["']?\)/)[1];
                let fullUrl;
                
                if (url.startsWith('http')) {
                    fullUrl = url;
                } else if (url.startsWith('//')) {
                    fullUrl = 'https:' + url;
                } else if (baseUrl) {
                    fullUrl = new URL(url, baseUrl).href;
                } else {
                    continue;
                }
                
                references.add(fullUrl);
            }
        }

        // Extract background images from CSS
        const imgMatches = cssContent.match(/url\(["']?([^"')]*\.(png|jpg|jpeg|gif|svg))["']?\)/gi);
        if (imgMatches) {
            for (const match of imgMatches) {
                const url = match.match(/url\(["']?([^"')]*)["']?\)/)[1];
                let fullUrl;
                
                if (url.startsWith('http')) {
                    fullUrl = url;
                } else if (url.startsWith('//')) {
                    fullUrl = 'https:' + url;
                } else if (baseUrl) {
                    fullUrl = new URL(url, baseUrl).href;
                } else {
                    continue;
                }
                
                references.add(fullUrl);
            }
        }

        return references;
    }

    /**
     * Create MHTML content with all dependencies
     */
    async createMHTML(htmlFile, outputFile) {
        console.log(`Creating comprehensive MHTML bundle for ${htmlFile}...`);
        
        const htmlPath = path.resolve(this.baseDir, htmlFile);
        const htmlDir = path.dirname(htmlPath);
        const htmlContent = fs.readFileSync(htmlPath, 'utf8');
        
        // Extract all referenced files
        const references = this.extractReferences(htmlContent, htmlDir);
        console.log(`Found ${references.local.size} local files and ${references.external.size} external resources`);
        
        // Fetch external resources
        const externalResources = [];
        for (const url of references.external) {
            const resource = await this.fetchExternalResource(url);
            if (resource) {
                externalResources.push({ url, resource });
                
                // If it's a CSS file, extract additional font/image references
                if (resource.contentType && resource.contentType.includes('text/css')) {
                    const cssContent = resource.data.toString();
                    const additionalRefs = await this.processCSSContent(cssContent, url);
                    
                    for (const additionalUrl of additionalRefs) {
                        if (!this.externalResources.has(additionalUrl)) {
                            const additionalResource = await this.fetchExternalResource(additionalUrl);
                            if (additionalResource) {
                                externalResources.push({ url: additionalUrl, resource: additionalResource });
                            }
                        }
                    }
                }
            }
        }
        
        console.log(`Fetched ${externalResources.length} external resources`);
        
        // Start building MHTML content
        let mhtmlContent = `MIME-Version: 1.0\r\n`;
        mhtmlContent += `Content-Type: multipart/related; boundary="${this.boundary}"\r\n`;
        mhtmlContent += `Subject: Phoenix Codex - ${path.basename(htmlFile)}\r\n`;
        mhtmlContent += `\r\n`;
        mhtmlContent += `This is a multi-part message in MIME format.\r\n`;
        mhtmlContent += `\r\n`;
        
        // Add main HTML file
        mhtmlContent += `--${this.boundary}\r\n`;
        mhtmlContent += `Content-Type: text/html; charset=UTF-8\r\n`;
        mhtmlContent += `Content-Location: ${path.basename(htmlFile)}\r\n`;
        mhtmlContent += `\r\n`;
        mhtmlContent += htmlContent;
        mhtmlContent += `\r\n`;
        
        // Add local files
        for (const filePath of references.local) {
            const fileData = this.encodeFile(filePath);
            if (fileData) {
                console.log(`Adding local: ${path.relative(this.baseDir, filePath)}`);
                mhtmlContent += `--${this.boundary}\r\n`;
                mhtmlContent += `Content-Type: ${fileData.contentType}\r\n`;
                mhtmlContent += `Content-Transfer-Encoding: ${fileData.encoding}\r\n`;
                mhtmlContent += `Content-Location: ${path.relative(htmlDir, filePath)}\r\n`;
                mhtmlContent += `\r\n`;
                mhtmlContent += fileData.content;
                mhtmlContent += `\r\n`;
            }
        }
        
        // Add external resources
        externalResources.forEach(({ url, resource }) => {
            console.log(`Adding external: ${url}`);
            mhtmlContent += `--${this.boundary}\r\n`;
            mhtmlContent += `Content-Type: ${resource.contentType}\r\n`;
            mhtmlContent += `Content-Transfer-Encoding: base64\r\n`;
            mhtmlContent += `Content-Location: ${url}\r\n`;
            mhtmlContent += `\r\n`;
            mhtmlContent += resource.data.toString('base64');
            mhtmlContent += `\r\n`;
        });
        
        // Close MHTML
        mhtmlContent += `--${this.boundary}--\r\n`;
        
        // Write output file
        fs.writeFileSync(outputFile, mhtmlContent);
        console.log(`MHTML bundle created: ${outputFile}`);
        console.log(`File size: ${(fs.statSync(outputFile).size / 1024 / 1024).toFixed(2)} MB`);
        console.log(`Total resources included: ${references.local.size + externalResources.length}`);
    }

    /**
     * Bundle all HTML files in the project
     */
    async bundleAll() {
        console.log('Phoenix Codex Enhanced MHTML Bundler');
        console.log('=====================================');
        
        // Find all HTML files
        const htmlFiles = [
            'index.html',
            'phoenix_codex_web.html',
            'PHOENIX_CODEX_OVERVIEW.html',
            'Amandamath+Tagbuilder.html'
        ].filter(file => fs.existsSync(file));
        
        if (htmlFiles.length === 0) {
            console.log('No HTML files found to bundle.');
            return;
        }
        
        // Create bundles directory
        const bundlesDir = 'bundles';
        if (!fs.existsSync(bundlesDir)) {
            fs.mkdirSync(bundlesDir);
        }
        
        // Bundle each HTML file
        for (const htmlFile of htmlFiles) {
            const baseName = path.basename(htmlFile, '.html');
            const outputFile = path.join(bundlesDir, `${baseName}.mhtml`);
            
            try {
                await this.createMHTML(htmlFile, outputFile);
                console.log(''); // Add spacing between files
            } catch (error) {
                console.error(`Error bundling ${htmlFile}:`, error.message);
            }
        }
        
        console.log('\nEnhanced MHTML bundling complete!');
        console.log(`Self-contained bundles created in: ${bundlesDir}/`);
        console.log('These MHTML files now include all external dependencies and work completely offline.');
    }
}

// Main execution
if (require.main === module) {
    const bundler = new MHTMLBundler();
    
    // Check for command line arguments
    const args = process.argv.slice(2);
    
    if (args.length >= 2) {
        // Bundle specific file
        const [inputFile, outputFile] = args;
        bundler.createMHTML(inputFile, outputFile).catch(console.error);
    } else if (args.length === 1) {
        // Bundle specific file with auto-generated output name
        const inputFile = args[0];
        const baseName = path.basename(inputFile, '.html');
        const outputFile = `${baseName}.mhtml`;
        bundler.createMHTML(inputFile, outputFile).catch(console.error);
    } else {
        // Bundle all HTML files
        bundler.bundleAll().catch(console.error);
    }
}

module.exports = MHTMLBundler;