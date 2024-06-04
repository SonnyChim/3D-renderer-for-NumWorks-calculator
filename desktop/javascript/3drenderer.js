
function main() {
    const canvas = document.getElementById("canvas");
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    const render = new renderer(canvas, 70);
    // render.test();
    // render.rotatingTriangle();
    // render.rotatingPyramid();
    // render.drawTri3d({x1:-141,y1:-173,z1:26,x2:-165,y2:-14,z2:-17,x3:-162,y3:30,z3:19},"rgb(0,0,0)")

    //((-150, 0 , 30),(-150,-50,-30),(-150,50,-30),(128,128,128)),
    //((-141,-173,26),(-165,-14,-17),(-162,30,19),(128,128,128)),
    //((-150, 0 , 30),(-150,-50,-30),(-150,50,-30),(128,128,128))
    const test =
        [
            { x1: -150, y1: 0, z1: 30, x2: -150, y2: -50, z2: -30, x3: -150, y3: 50, z3: -30, r: 128, g: 18, b: 128 },
            { x1: -141, y1: -83, z1: 26, x2: -165, y2: -14, z2: -17, x3: -162, y3: 30, z3: 19, r: 18, g: 128, b: 128 }
        ];
    // render.drawScene(test);
    document.addEventListener("mousemove", function (event) { render.setFOV(event.clientX / window.innerWidth * 178 + 1); })
}

class renderer {
    constructor(canvas, fov) {
        this.canvas = canvas;
        this.ctx = this.canvas.getContext("2d");
        this.isRunning = false;
        this.height = canvas.height;
        this.width = canvas.width;
        this.setFOV(fov);
        this.rotation = 0;
        this.offsetCache = undefined;
        this.canvas.addEventListener("dragenter", this.stopPropagationPreventDefault)
        this.canvas.addEventListener("dragover", this.stopPropagationPreventDefault)
        this.canvas.addEventListener("drop", (e) => { this.loadFile(e).then((res) => { this.processFile(res[1], res[0]); this.makeSceneFromFiles() }) })
        this.canvas.addEventListener("mousedown", this.toggleRenderer.bind(this))
        // window.addEventListener("blur",() => {if (this.isRunning) {this.disableRenderer.bind(this)();window.addEventListener("focus", this.enableRenderer.bind(this), {once:true})}});
        this.sortingTolerance = 0.001
    }
    setFOV(fov) {
        const halfScreenWidth = Math.tan(this.radians(fov / 2)) * 100;
        const halfScreenHeight = halfScreenWidth * this.height / this.width;
        // virtual screen for projection
        this.screen = { y1: -halfScreenWidth, z1: -halfScreenHeight, y2: halfScreenWidth, z2: halfScreenHeight, x: -100 };
    }
    drawTri2d(tri2d, color) {
        this.ctx.fillStyle = color;
        this.ctx.strokeStyle = color;
        const newPath = new Path2D("M" + tri2d.x1 + " " + tri2d.y1 + "L" + tri2d.x2 + " " + tri2d.y2 + "L" + tri2d.x3 + " " + tri2d.y3 + "Z");
        this.ctx.fill(newPath);
        // this.ctx.stroke(newPath);
    }
    project(x, y, z) {
        if (x >= 0) {
            return null;
        }
        return {
            x: Math.trunc((this.screen.y1 - (y / -x) * -this.screen.x) * (this.width / (this.screen.y1 - this.screen.y2))),
            y: Math.trunc((this.screen.z1 + (z / -x) * -this.screen.x) * (this.height / (this.screen.z1 - this.screen.z2)))
        };

    }
    drawTri3d(tri3d, color) {
        const tri2d = {};
        ({ x: tri2d.x1, y: tri2d.y1 } = this.project(tri3d.x1, tri3d.y1, tri3d.z1) ?? { x: undefined, y: undefined });
        ({ x: tri2d.x2, y: tri2d.y2 } = this.project(tri3d.x2, tri3d.y2, tri3d.z2) ?? { x: undefined, y: undefined });
        ({ x: tri2d.x3, y: tri2d.y3 } = this.project(tri3d.x3, tri3d.y3, tri3d.z3) ?? { x: undefined, y: undefined });
        for (const key in tri2d) {
            if (tri2d[key] == undefined) {
                // console.log("clipped tri");
                return
            };
        };
        this.drawTri2d(tri2d, color);
    }
    rgbToCSS(rgb) {
        return "rgb(" + rgb[0] + "," + rgb[1] + "," + rgb[2] + ")";
    }
    radians(degrees) {
        return degrees * Math.PI / 180;
    }
    async rotatingTriangle() {
        let running = true;
        document.addEventListener("click", () => { running = false; });
        let angle = 0;
        while (running) {
            this.ctx.clearRect(0, 0, this.width, this.height);
            const coords = {
                x1: -150,
                y1: 0,
                z1: 30,
                x2: -150 + 50 * Math.sin(this.radians(angle + 180)),
                y2: 50 * Math.cos(this.radians(angle + 180)),
                z2: -30,
                x3: -150 + 50 * Math.sin(this.radians(angle)),
                y3: 50 * Math.cos(this.radians(angle)),
                z3: -30
            };
            this.drawTri3d(coords, "rgb(128,128,128)");
            angle += 1;
            await sleep(0);
        }
    }
    sortTris(scene) {
        const mapped = scene.map((element, index) => {
            const vertexDistances =
                [
                    element.x1 * element.x1 + element.y1 * element.y1 + element.z1 * element.z1,
                    element.x2 * element.x2 + element.y2 * element.y2 + element.z2 * element.z2,
                    element.x3 * element.x3 + element.y3 * element.y3 + element.z3 * element.z3,
                ];
            const closestVertex = Math.min(...vertexDistances);
            const averageDistance = vertexDistances.reduce((accumulator, currentValue) => accumulator + currentValue);
            return [closestVertex, averageDistance, index];
        })
        mapped.sort((a, b) => {
            if (Math.abs(a[0] - b[0]) < this.sortingTolerance) { return b[1] - a[1]; };
            return b[0] - a[0];
        })
        return mapped.map((element) => scene[element[2]])
    }
    drawScene(scene) {
        this.ctx.clearRect(0, 0, this.width, this.height);
        const sortedScene = this.sortTris(scene);
        // for (const tri of sortedScene) {
        //     this.drawTri3d(tri, this.rgbToCSS([tri.r, tri.g, tri.b]));
        // };
        const sortedSceneLength = sortedScene.length;
        for (let i = 0; i < sortedSceneLength; ++i) {
            const tri = sortedScene[i];
            this.drawTri3d(tri, this.rgbToCSS([tri.r, tri.g, tri.b]));
        };
    }
    rotatingPyramid() {
        let running = true;
        document.addEventListener("click", () => { running = false; }, { once: true });
        let angle = 0;
        let scene = [null, null, null, null]
        window.requestAnimationFrame(function drawPyramid() {
            this.ctx.clearRect(0, 0, this.width, this.height);
            for (let i = 0; i < 4; i++) {
                scene[i] = {
                    x1: -150,
                    y1: 0,
                    z1: 30,
                    x2: -150 + 50 * Math.sin(this.radians(angle + 90 + i * 90)),
                    y2: 50 * Math.cos(this.radians(angle + 90 + i * 90)),
                    z2: -30,
                    x3: -150 + 50 * Math.sin(this.radians(angle + i * 90)),
                    y3: 50 * Math.cos(this.radians(angle + i * 90)),
                    z3: -30,
                    r: 256 - 128 * ((angle + 90 * i + 180) % 360) / 360,
                    g: 256 - 128 * ((angle + 90 * i + 180) % 360) / 360,
                    b: 256 - 128 * ((angle + 90 * i + 180) % 360) / 360
                };
            }
            this.drawScene(scene)
            angle += 1;
            if (running) {
                window.requestAnimationFrame(drawPyramid.bind(this));
            }
        }.bind(this))
    }
    stopPropagationPreventDefault(e) {
        e.stopPropagation();
        e.preventDefault();
    }
    loadFile(e) {
        this.stopPropagationPreventDefault(e);
        const dt = e.dataTransfer;
        const files = dt.files;
        const file = files[0];
        const reader = new FileReader();
        return new Promise((resolve) => {
            if (file.name.slice(-4) === ".obj") {
                reader.addEventListener("load", () => { resolve(["obj", reader.result]); });
            } else if (file.name.slice(-4) === ".mtl") {
                reader.addEventListener("load", () => { resolve(["mtl", reader.result]); });
            }
            reader.readAsText(file);
        })
    }
    processFile(file, type) {
        if (type === "obj") {
            // .obj file
            // scale: 100
            // forward axis: y
            // up axis: z
            const vertices = file.split("\n").filter((line) => { return line.slice(0, 2) === "v " }).map((line) => { return line.split(/\s+/).slice(1, 4).map((val) => { return parseFloat(val) }) });
            const faces = file.split("\n").filter((line) => { return line.slice(0, 2) === "f " }).map((line) => { return line.split(/\s+/).filter((val) => { return val }).slice(1).map((val) => { return parseInt(val.split("/")[0]) }) })
            this.triangleCoords = faces.map((face) => { return face.map((index) => { return vertices[index - 1] }) });
            this.offsetCache = undefined;
            this.materialIndeces = [];
            let index = 0;
            file.split("\n").forEach((val) => { if (val.slice(0, 7) === "usemtl ") { this.materialIndeces.push([index, val.slice(7)]) } else if (val.slice(0, 2) === "f " ) {++index}});
            // console.log(this.triangleCoords);
        } else if (type === "mtl") {
            this.materials = {}
            let lastMaterial;
            file.split("\n").forEach((line) => { if (line.slice(0, 7) === "newmtl ") { lastMaterial = line.slice(7); } else if (line.slice(0, 3) === "Kd ") { this.materials[lastMaterial] = line.slice(3).split(/\s+/).map((val) => { return Math.round(parseFloat(val) * 255) }) } })
            // console.log(this.materials);
        }
    }
    getRecommendedOffset() {
        if (this.offsetCache) {
            return this.offsetCache;
        }
        let bounds = {
            xl: Infinity,
            xh: -Infinity,
            yl: Infinity,
            yh: -Infinity,
            zl: Infinity,
            zh: -Infinity
        };
        for (const tri of this.triangleCoords) {
            if (Math.min(tri[0][0], tri[1][0], tri[2][0]) < bounds.xl) {
                bounds.xl = Math.min(tri[0][0], tri[1][0], tri[2][0]);
            }
            if (Math.max(tri[0][0], tri[1][0], tri[2][0]) > bounds.xh) {
                bounds.xh = Math.max(tri[0][0], tri[1][0], tri[2][0]);
            }
            if (Math.min(tri[0][1], tri[1][1], tri[2][1]) < bounds.yl) {
                bounds.yl = Math.min(tri[0][1], tri[1][1], tri[2][1]);
            }
            if (Math.max(tri[0][1], tri[1][1], tri[2][1]) > bounds.yh) {
                bounds.yh = Math.max(tri[0][1], tri[1][1], tri[2][1]);
            }
            if (Math.min(tri[0][2], tri[1][2], tri[2][2]) < bounds.zl) {
                bounds.zl = Math.min(tri[0][2], tri[1][2], tri[2][2]);
            }
            if (Math.max(tri[0][2], tri[1][2], tri[2][2]) > bounds.zh) {
                bounds.zh = Math.max(tri[0][2], tri[1][2], tri[2][2]);
            }
        }
        const origin = {
            x: Math.round((bounds.xl + bounds.xh) / 2),
            y: Math.round((bounds.yl + bounds.yh) / 2),
            z: Math.round((bounds.zl + bounds.zh) / 2)
        };
        const size = {
            y: bounds.yh - bounds.yl,
            z: bounds.zh - bounds.zl
        };
        const offset = {
            x: -origin.x - size.y / 0.25,
            y: -origin.y,
            z: -origin.z,
            orx: -origin.x,
            sy: size.y
        };
        this.offsetCache = offset;
        return offset;
    }
    makeSceneFromFiles(offset = this.getRecommendedOffset()) {
        if (this.triangleCoords && this.materials && this.materialIndeces) {
            this.scene = this.triangleCoords.map((tri, index) => {
                const colors = this.materials[this.materialIndeces.findLast((val) => {
                    return index >= val[0]
                })[1]];
                return {
                    x1: tri[0][0] + offset.x,
                    y1: tri[0][1] + offset.y,
                    z1: tri[0][2] + offset.z,
                    x2: tri[1][0] + offset.x,
                    y2: tri[1][1] + offset.y,
                    z2: tri[1][2] + offset.z,
                    x3: tri[2][0] + offset.x,
                    y3: tri[2][1] + offset.y,
                    z3: tri[2][2] + offset.z,
                    r: colors[0],
                    g: colors[1],
                    b: colors[2]
                }
            })
        } else if (this.triangleCoords) {
            this.scene = this.triangleCoords.map((tri) => {
                return {
                    x1: tri[0][0] + offset.x,
                    y1: tri[0][1] + offset.y,
                    z1: tri[0][2] + offset.z,
                    x2: tri[1][0] + offset.x,
                    y2: tri[1][1] + offset.y,
                    z2: tri[1][2] + offset.z,
                    x3: tri[2][0] + offset.x,
                    y3: tri[2][1] + offset.y,
                    z3: tri[2][2] + offset.z,
                    r: Math.floor((tri[0][0] - offset.orx) / offset.sy * 256) + 128,
                    g: Math.floor((tri[0][1] - offset.y) / offset.sy * 256) + 128,
                    b: Math.floor((tri[0][2] - offset.z) / offset.sy * 256) + 128
                }
            })
        }
    }
    makeRotatedSceneFromFiles(degrees, offset = this.getRecommendedOffset()) {
        const radians = this.radians(degrees)
        if (this.triangleCoords && this.materials && this.materialIndeces) {
            this.scene = this.triangleCoords.map((tri, index) => {
                const colors = this.materials[this.materialIndeces.findLast((val) => {
                    return index >= val[0]
                })[1]];
                const distances = tri.map((vertex) => { return Math.sqrt(vertex[0] * vertex[0] + vertex[1] * vertex[1]) })
                const angles = tri.map((vertex) => {
                    if (vertex[1] > 0) {
                        return Math.atan(vertex[0] / vertex[1])
                    } else if (vertex[1] == 0) {
                        return Math.PI / 2
                    } else {
                        return Math.atan(vertex[0] / vertex[1]) + Math.PI
                    }
                })
                return {
                    x1: distances[0] * Math.sin(radians + angles[0]) + offset.x,
                    y1: distances[0] * Math.cos(radians + angles[0]) + offset.y,
                    z1: tri[0][2] + offset.z,
                    x2: distances[1] * Math.sin(radians + angles[1]) + offset.x,
                    y2: distances[1] * Math.cos(radians + angles[1]) + offset.y,
                    z2: tri[1][2] + offset.z,
                    x3: distances[2] * Math.sin(radians + angles[2]) + offset.x,
                    y3: distances[2] * Math.cos(radians + angles[2]) + offset.y,
                    z3: tri[2][2] + offset.z,
                    r: colors[0],
                    g: colors[1],
                    b: colors[2]
                }
            })
        } else if (this.triangleCoords) {
            this.scene = this.triangleCoords.map((tri) => {
                const distances = tri.map((vertex) => { return Math.sqrt(vertex[0] * vertex[0] + vertex[1] * vertex[1]) })
                const angles = tri.map((vertex) => {
                    if (vertex[1] > 0) {
                        return Math.atan(vertex[0] / vertex[1])
                    } else if (vertex[1] == 0) {
                        return Math.PI / 2
                    } else {
                        return Math.atan(vertex[0] / vertex[1]) + Math.PI
                    }
                })
                return {
                    x1: distances[0] * Math.sin(this.radians(degrees) + angles[0]) + offset.x,
                    y1: distances[0] * Math.cos(this.radians(degrees) + angles[0]) + offset.y,
                    z1: tri[0][2] + offset.z,
                    x2: distances[1] * Math.sin(this.radians(degrees) + angles[1]) + offset.x,
                    y2: distances[1] * Math.cos(this.radians(degrees) + angles[1]) + offset.y,
                    z2: tri[1][2] + offset.z,
                    x3: distances[2] * Math.sin(this.radians(degrees) + angles[2]) + offset.x,
                    y3: distances[2] * Math.cos(this.radians(degrees) + angles[2]) + offset.y,
                    z3: tri[2][2] + offset.z,
                    r: Math.floor((tri[0][0] - offset.orx) / offset.sy * 256) + 128,
                    g: Math.floor((tri[0][1] - offset.y) / offset.sy * 256) + 128,
                    b: Math.floor((tri[0][2] - offset.z) / offset.sy * 256) + 128
                }
            })
        }
    }
    enableRenderer() {
        if (!this.isRunning){
            this.isRunning = true;
            this.initializeRenderer()
        }
    }
    disableRenderer() {
        this.isRunning = false;
    }
    toggleRenderer() {
        if (this.isRunning) {
            this.disableRenderer();
        } else {
            this.enableRenderer();
        }
    }
    renderFrame() {
        // this.ctx.clearRect(0, 0, this.width, this.height);
        if (this.scene) {
            // this.drawScene(this.scene);
            this.makeRotatedSceneFromFiles(this.rotation);
            this.drawScene(this.scene);
            this.rotation += 1;
        }
        if (this.isRunning) {
            window.requestAnimationFrame(this.renderFrame.bind(this));
        }
    }
    initializeRenderer() {
        window.requestAnimationFrame(this.renderFrame.bind(this));
    }
    test() {
        this.ctx.fillStyle = "blue";
        const path = new Path2D("M 100 100 L 200 100 L 200 200 Z");
        this.ctx.fill(path);

    }
}
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
main();