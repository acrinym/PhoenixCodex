// Phoenix Codex - Three.js Visualization Module
import * as THREE from 'https://cdn.skypack.dev/three@0.162.0';
import { DataManager } from './utils.js';

class VisualizationManager {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.animationId = null;
        this.isInitialized = false;
        this.currentVisualization = null;
        this.performanceMode = 'balanced';
        this.animationsEnabled = true;
        this.animationSpeed = 1.0;
        this.colorScheme = 'phoenix';
        
        this.dataManager = new DataManager();
        this.colorSchemes = {
            phoenix: {
                primary: 0xff6b35,
                secondary: 0xf7931e,
                accent: 0xffd23f,
                background: 0x2c1810
            },
            ocean: {
                primary: 0x0066cc,
                secondary: 0x0099ff,
                accent: 0x00ccff,
                background: 0x003366
            },
            forest: {
                primary: 0x2d5a27,
                secondary: 0x4a7c59,
                accent: 0x6b8e23,
                background: 0x1a3d1a
            },
            sunset: {
                primary: 0xff8c42,
                secondary: 0xff6b6b,
                accent: 0xffd93d,
                background: 0x8b4513
            }
        };
    }
    
    init() {
        if (this.isInitialized) return;
        
        const container = document.getElementById('three-container');
        if (!container) return;
        
        this.setupScene(container);
        this.setupCamera();
        this.setupRenderer(container);
        this.setupControls();
        this.setupLights();
        this.setupEventListeners();
        
        this.isInitialized = true;
        this.animate();
        
        // Load initial visualization
        this.loadVisualization('network');
    }
    
    setupScene(container) {
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(this.colorSchemes[this.colorScheme].background);
        
        // Add fog for depth
        this.scene.fog = new THREE.Fog(this.colorSchemes[this.colorScheme].background, 50, 200);
    }
    
    setupCamera() {
        const container = document.getElementById('three-container');
        const aspect = container.clientWidth / container.clientHeight;
        
        this.camera = new THREE.PerspectiveCamera(75, aspect, 0.1, 1000);
        this.camera.position.set(0, 0, 50);
    }
    
    setupRenderer(container) {
        this.renderer = new THREE.WebGLRenderer({ 
            antialias: true,
            alpha: true 
        });
        
        this.renderer.setSize(container.clientWidth, container.clientHeight);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        
        container.appendChild(this.renderer.domElement);
    }
    
    setupControls() {
        // Simple orbit controls
        this.controls = {
            rotation: { x: 0, y: 0 },
            zoom: 50,
            isMouseDown: false,
            lastMousePosition: { x: 0, y: 0 }
        };
    }
    
    setupLights() {
        // Ambient light
        const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
        this.scene.add(ambientLight);
        
        // Directional light
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(10, 10, 5);
        directionalLight.castShadow = true;
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        this.scene.add(directionalLight);
        
        // Point light for accent
        const pointLight = new THREE.PointLight(this.colorSchemes[this.colorScheme].accent, 0.5);
        pointLight.position.set(-10, 10, -10);
        this.scene.add(pointLight);
    }
    
    setupEventListeners() {
        const container = document.getElementById('three-container');
        
        // Mouse controls
        container.addEventListener('mousedown', (e) => {
            this.controls.isMouseDown = true;
            this.controls.lastMousePosition = { x: e.clientX, y: e.clientY };
        });
        
        container.addEventListener('mousemove', (e) => {
            if (!this.controls.isMouseDown) return;
            
            const deltaX = e.clientX - this.controls.lastMousePosition.x;
            const deltaY = e.clientY - this.controls.lastMousePosition.y;
            
            this.controls.rotation.y += deltaX * 0.01;
            this.controls.rotation.x += deltaY * 0.01;
            
            this.controls.lastMousePosition = { x: e.clientX, y: e.clientY };
        });
        
        container.addEventListener('mouseup', () => {
            this.controls.isMouseDown = false;
        });
        
        // Wheel zoom
        container.addEventListener('wheel', (e) => {
            e.preventDefault();
            this.controls.zoom += e.deltaY * 0.1;
            this.controls.zoom = Math.max(10, Math.min(100, this.controls.zoom));
        });
        
        // Window resize
        window.addEventListener('resize', () => {
            this.onWindowResize();
        });
        
        // Control panel events
        const vizTypeSelect = document.getElementById('viz-type');
        if (vizTypeSelect) {
            vizTypeSelect.addEventListener('change', (e) => {
                this.loadVisualization(e.target.value);
            });
        }
        
        const colorSchemeSelect = document.getElementById('color-scheme');
        if (colorSchemeSelect) {
            colorSchemeSelect.addEventListener('change', (e) => {
                this.changeColorScheme(e.target.value);
            });
        }
        
        const animationSpeedRange = document.getElementById('animation-speed');
        if (animationSpeedRange) {
            animationSpeedRange.addEventListener('input', (e) => {
                this.animationSpeed = parseFloat(e.target.value);
            });
        }
        
        const resetCameraBtn = document.getElementById('reset-camera');
        if (resetCameraBtn) {
            resetCameraBtn.addEventListener('click', () => {
                this.resetCamera();
            });
        }
    }
    
    loadVisualization(type) {
        this.clearScene();
        this.currentVisualization = type;
        
        switch (type) {
            case 'network':
                this.createNetworkGraph();
                break;
            case 'timeline-3d':
                this.create3DTimeline();
                break;
            case 'content-clusters':
                this.createContentClusters();
                break;
            case 'relationship-map':
                this.createRelationshipMap();
                break;
            default:
                this.createNetworkGraph();
        }
    }
    
    createNetworkGraph() {
        const data = this.dataManager.getData();
        if (!data || data.length === 0) return;
        
        // Group by source
        const sourceGroups = {};
        data.forEach(item => {
            if (!sourceGroups[item.source]) {
                sourceGroups[item.source] = [];
            }
            sourceGroups[item.source].push(item);
        });
        
        const sources = Object.keys(sourceGroups);
        const colors = this.getColorPalette();
        
        // Create nodes
        sources.forEach((source, index) => {
            const group = sourceGroups[source];
            const nodeGeometry = new THREE.SphereGeometry(1 + group.length * 0.1, 16, 16);
            const nodeMaterial = new THREE.MeshPhongMaterial({ 
                color: colors[index % colors.length],
                transparent: true,
                opacity: 0.8
            });
            
            const node = new THREE.Mesh(nodeGeometry, nodeMaterial);
            
            // Position in a circle
            const angle = (index / sources.length) * Math.PI * 2;
            const radius = 15;
            node.position.set(
                Math.cos(angle) * radius,
                Math.sin(angle) * radius,
                0
            );
            
            node.userData = { source, count: group.length };
            this.scene.add(node);
            
            // Add text label
            this.addTextLabel(source, node.position);
        });
        
        // Create connections between related sources
        this.createConnections(sources, sourceGroups);
    }
    
    create3DTimeline() {
        const data = this.dataManager.getData();
        if (!data || data.length === 0) return;
        
        // Sort by date
        const sortedData = data.sort((a, b) => new Date(a.date) - new Date(b.date));
        
        const colors = this.getColorPalette();
        const typeColors = {};
        const types = [...new Set(data.map(item => item.type))];
        types.forEach((type, index) => {
            typeColors[type] = colors[index % colors.length];
        });
        
        // Create timeline points
        sortedData.forEach((item, index) => {
            const geometry = new THREE.SphereGeometry(0.5, 8, 8);
            const material = new THREE.MeshPhongMaterial({ 
                color: typeColors[item.type] || colors[0],
                transparent: true,
                opacity: 0.7
            });
            
            const point = new THREE.Mesh(geometry, material);
            
            // Position along timeline
            const timelineLength = 40;
            const progress = index / (sortedData.length - 1);
            point.position.set(
                (progress - 0.5) * timelineLength,
                Math.sin(progress * Math.PI * 4) * 5,
                Math.cos(progress * Math.PI * 2) * 5
            );
            
            point.userData = { item, index };
            this.scene.add(point);
            
            // Add connecting lines
            if (index > 0) {
                const prevPoint = sortedData[index - 1];
                const lineGeometry = new THREE.BufferGeometry().setFromPoints([
                    new THREE.Vector3(
                        ((index - 1) / (sortedData.length - 1) - 0.5) * timelineLength,
                        Math.sin(((index - 1) / (sortedData.length - 1)) * Math.PI * 4) * 5,
                        Math.cos(((index - 1) / (sortedData.length - 1)) * Math.PI * 2) * 5
                    ),
                    point.position
                ]);
                
                const lineMaterial = new THREE.LineBasicMaterial({ 
                    color: 0x666666,
                    transparent: true,
                    opacity: 0.3
                });
                
                const line = new THREE.Line(lineGeometry, lineMaterial);
                this.scene.add(line);
            }
        });
        
        // Add timeline axis
        const axisGeometry = new THREE.BufferGeometry().setFromPoints([
            new THREE.Vector3(-timelineLength / 2, 0, 0),
            new THREE.Vector3(timelineLength / 2, 0, 0)
        ]);
        
        const axisMaterial = new THREE.LineBasicMaterial({ color: 0x888888 });
        const axis = new THREE.Line(axisGeometry, axisMaterial);
        this.scene.add(axis);
    }
    
    createContentClusters() {
        const data = this.dataManager.getData();
        if (!data || data.length === 0) return;
        
        // Group by tags
        const tagGroups = {};
        data.forEach(item => {
            item.tags.forEach(tag => {
                if (!tagGroups[tag]) {
                    tagGroups[tag] = [];
                }
                tagGroups[tag].push(item);
            });
        });
        
        const tags = Object.keys(tagGroups);
        const colors = this.getColorPalette();
        
        // Create clusters
        tags.forEach((tag, index) => {
            const group = tagGroups[tag];
            const clusterGeometry = new THREE.SphereGeometry(2 + group.length * 0.2, 16, 16);
            const clusterMaterial = new THREE.MeshPhongMaterial({ 
                color: colors[index % colors.length],
                transparent: true,
                opacity: 0.6
            });
            
            const cluster = new THREE.Mesh(clusterGeometry, clusterMaterial);
            
            // Position in a spiral
            const angle = (index / tags.length) * Math.PI * 4;
            const radius = 8 + index * 2;
            cluster.position.set(
                Math.cos(angle) * radius,
                Math.sin(angle) * radius,
                index * 2
            );
            
            cluster.userData = { tag, count: group.length };
            this.scene.add(cluster);
            
            // Add text label
            this.addTextLabel(`${tag} (${group.length})`, cluster.position);
            
            // Add smaller nodes for individual items
            group.forEach((item, itemIndex) => {
                const itemGeometry = new THREE.SphereGeometry(0.3, 8, 8);
                const itemMaterial = new THREE.MeshPhongMaterial({ 
                    color: colors[index % colors.length],
                    transparent: true,
                    opacity: 0.8
                });
                
                const itemNode = new THREE.Mesh(itemGeometry, itemMaterial);
                
                // Position around cluster
                const itemAngle = (itemIndex / group.length) * Math.PI * 2;
                const itemRadius = 3 + group.length * 0.1;
                itemNode.position.set(
                    cluster.position.x + Math.cos(itemAngle) * itemRadius,
                    cluster.position.y + Math.sin(itemAngle) * itemRadius,
                    cluster.position.z
                );
                
                itemNode.userData = { item };
                this.scene.add(itemNode);
            });
        });
    }
    
    createRelationshipMap() {
        const data = this.dataManager.getData();
        if (!data || data.length === 0) return;
        
        // Create relationship matrix
        const sources = [...new Set(data.map(item => item.source))];
        const relationships = {};
        
        sources.forEach(source1 => {
            relationships[source1] = {};
            sources.forEach(source2 => {
                if (source1 !== source2) {
                    // Find common tags between sources
                    const source1Tags = new Set();
                    const source2Tags = new Set();
                    
                    data.filter(item => item.source === source1).forEach(item => {
                        item.tags.forEach(tag => source1Tags.add(tag));
                    });
                    
                    data.filter(item => item.source === source2).forEach(item => {
                        item.tags.forEach(tag => source2Tags.add(tag));
                    });
                    
                    const commonTags = [...source1Tags].filter(tag => source2Tags.has(tag));
                    relationships[source1][source2] = commonTags.length;
                }
            });
        });
        
        const colors = this.getColorPalette();
        
        // Create nodes for sources
        sources.forEach((source, index) => {
            const nodeGeometry = new THREE.SphereGeometry(1.5, 16, 16);
            const nodeMaterial = new THREE.MeshPhongMaterial({ 
                color: colors[index % colors.length],
                transparent: true,
                opacity: 0.8
            });
            
            const node = new THREE.Mesh(nodeGeometry, nodeMaterial);
            
            // Position in a grid
            const gridSize = Math.ceil(Math.sqrt(sources.length));
            const spacing = 8;
            node.position.set(
                (index % gridSize - (gridSize - 1) / 2) * spacing,
                (Math.floor(index / gridSize) - (gridSize - 1) / 2) * spacing,
                0
            );
            
            node.userData = { source };
            this.scene.add(node);
            
            // Add text label
            this.addTextLabel(source, node.position);
        });
        
        // Create relationship lines
        sources.forEach((source1, index1) => {
            sources.forEach((source2, index2) => {
                if (index1 < index2 && relationships[source1][source2] > 0) {
                    const strength = relationships[source1][source2];
                    const lineGeometry = new THREE.BufferGeometry().setFromPoints([
                        new THREE.Vector3(
                            (index1 % gridSize - (gridSize - 1) / 2) * spacing,
                            (Math.floor(index1 / gridSize) - (gridSize - 1) / 2) * spacing,
                            0
                        ),
                        new THREE.Vector3(
                            (index2 % gridSize - (gridSize - 1) / 2) * spacing,
                            (Math.floor(index2 / gridSize) - (gridSize - 1) / 2) * spacing,
                            0
                        )
                    ]);
                    
                    const lineMaterial = new THREE.LineBasicMaterial({ 
                        color: 0xffffff,
                        transparent: true,
                        opacity: Math.min(0.8, strength * 0.2)
                    });
                    
                    const line = new THREE.Line(lineGeometry, lineMaterial);
                    this.scene.add(line);
                }
            });
        });
    }
    
    createConnections(sources, sourceGroups) {
        const colors = this.getColorPalette();
        
        sources.forEach((source1, index1) => {
            sources.forEach((source2, index2) => {
                if (index1 < index2) {
                    // Find common tags
                    const source1Tags = new Set();
                    const source2Tags = new Set();
                    
                    sourceGroups[source1].forEach(item => {
                        item.tags.forEach(tag => source1Tags.add(tag));
                    });
                    
                    sourceGroups[source2].forEach(item => {
                        item.tags.forEach(tag => source2Tags.add(tag));
                    });
                    
                    const commonTags = [...source1Tags].filter(tag => source2Tags.has(tag));
                    
                    if (commonTags.length > 0) {
                        const angle1 = (index1 / sources.length) * Math.PI * 2;
                        const angle2 = (index2 / sources.length) * Math.PI * 2;
                        const radius = 15;
                        
                        const lineGeometry = new THREE.BufferGeometry().setFromPoints([
                            new THREE.Vector3(
                                Math.cos(angle1) * radius,
                                Math.sin(angle1) * radius,
                                0
                            ),
                            new THREE.Vector3(
                                Math.cos(angle2) * radius,
                                Math.sin(angle2) * radius,
                                0
                            )
                        ]);
                        
                        const lineMaterial = new THREE.LineBasicMaterial({ 
                            color: colors[Math.min(index1, index2) % colors.length],
                            transparent: true,
                            opacity: Math.min(0.6, commonTags.length * 0.2)
                        });
                        
                        const line = new THREE.Line(lineGeometry, lineMaterial);
                        this.scene.add(line);
                    }
                }
            });
        });
    }
    
    addTextLabel(text, position) {
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        canvas.width = 256;
        canvas.height = 64;
        
        context.fillStyle = 'white';
        context.font = '24px Inter';
        context.textAlign = 'center';
        context.fillText(text, 128, 32);
        
        const texture = new THREE.CanvasTexture(canvas);
        const material = new THREE.SpriteMaterial({ map: texture });
        const sprite = new THREE.Sprite(material);
        
        sprite.position.copy(position);
        sprite.position.y += 2;
        sprite.scale.set(4, 1, 1);
        
        this.scene.add(sprite);
    }
    
    getColorPalette() {
        const scheme = this.colorSchemes[this.colorScheme];
        return [scheme.primary, scheme.secondary, scheme.accent];
    }
    
    changeColorScheme(scheme) {
        this.colorScheme = scheme;
        this.scene.background = new THREE.Color(this.colorSchemes[scheme].background);
        this.scene.fog = new THREE.Fog(this.colorSchemes[scheme].background, 50, 200);
        
        // Reload current visualization with new colors
        if (this.currentVisualization) {
            this.loadVisualization(this.currentVisualization);
        }
    }
    
    setPerformanceMode(mode) {
        this.performanceMode = mode;
        
        switch (mode) {
            case 'performance':
                this.renderer.setPixelRatio(1);
                break;
            case 'quality':
                this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
                break;
            default:
                this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
        }
    }
    
    setAnimationsEnabled(enabled) {
        this.animationsEnabled = enabled;
    }
    
    resetCamera() {
        this.camera.position.set(0, 0, 50);
        this.controls.rotation = { x: 0, y: 0 };
        this.controls.zoom = 50;
    }
    
    clearScene() {
        // Remove all objects except lights
        const objectsToRemove = [];
        this.scene.traverse((object) => {
            if (object.type !== 'Light' && object.type !== 'AmbientLight' && 
                object.type !== 'DirectionalLight' && object.type !== 'PointLight') {
                objectsToRemove.push(object);
            }
        });
        
        objectsToRemove.forEach(object => {
            this.scene.remove(object);
        });
    }
    
    onWindowResize() {
        const container = document.getElementById('three-container');
        if (!container) return;
        
        const width = container.clientWidth;
        const height = container.clientHeight;
        
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        
        this.renderer.setSize(width, height);
    }
    
    animate() {
        this.animationId = requestAnimationFrame(() => this.animate());
        
        if (!this.isInitialized) return;
        
        // Update camera based on controls
        this.camera.position.x = Math.sin(this.controls.rotation.y) * this.controls.zoom;
        this.camera.position.z = Math.cos(this.controls.rotation.y) * this.controls.zoom;
        this.camera.position.y = Math.sin(this.controls.rotation.x) * this.controls.zoom;
        this.camera.lookAt(0, 0, 0);
        
        // Animate scene objects
        if (this.animationsEnabled) {
            this.scene.traverse((object) => {
                if (object.type === 'Mesh' && object.userData) {
                    object.rotation.y += 0.01 * this.animationSpeed;
                    object.position.y += Math.sin(Date.now() * 0.001 + object.position.x) * 0.01 * this.animationSpeed;
                }
            });
        }
        
        this.renderer.render(this.scene, this.camera);
    }
    
    destroy() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        
        if (this.renderer) {
            this.renderer.dispose();
        }
        
        this.isInitialized = false;
    }
}

export { VisualizationManager }; 