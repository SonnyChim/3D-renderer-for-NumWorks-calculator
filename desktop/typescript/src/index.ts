

class renderer {
    
}

class Tri3d implements ITri3d {
    x1: number;
    y1: number;
    z1: number;
    x2: number;
    y2: number;
    z2: number;
    x3: number;
    y3: number;
    z3: number;
    constructor(x1: number, y1: number, z1: number, x2: number, y2: number, z2: number, x3: number, y3: number, z3: number) {
        this.x1 = x1;
        this.y1 = y1;
        this.z1 = z1;
        this.x2 = x2;
        this.y2 = y2;
        this.z2 = z2;
        this.x3 = x3;
        this.y3 = y3;
        this.z3 = z3;
    }
    project(screen: ProjectionScreen): Tri2d | undefined{
        if (this.x1 >= 0 || this.x2 >= 0 || this.x3 >= 0) {
            return undefined;
        }
        return {
            x1: Math.trunc((screen.y1 - (this.y1 / -this.x1)) * screen.widthMultiplier),
            y1: Math.trunc((screen.z1 + (this.z1 / -this.x1)) * screen.heightMultiplier),
            x2: Math.trunc((screen.y1 - (this.y2 / -this.x2)) * screen.widthMultiplier),
            y2: Math.trunc((screen.z1 + (this.z2 / -this.x2)) * screen.heightMultiplier),
            x3: Math.trunc((screen.y1 - (this.y3 / -this.x3)) * screen.widthMultiplier),
            y3: Math.trunc((screen.z1 + (this.z3 / -this.x3)) * screen.heightMultiplier),
        }
    }
    
}

class ProjectionScreen implements IProjectionScreen{
    y1!: number;
    z1!: number;
    y2!: number;
    z2!: number;
    x!: number;
    widthMultiplier!: number;
    heightMultiplier!: number;
    constructor(fov: number, height: number, width: number) {
        this.setFOV(fov,height,width);
    }
    public setFOV(fov: number, height: number, width: number): void {
        const halfScreenWidth = Math.tan(radians(fov / 2));
        const halfScreenHeight = halfScreenWidth * height / width;
        this.y1 = -halfScreenWidth;
        this.z1 = -halfScreenHeight;
        this.y2 = halfScreenWidth;
        this.z2 = halfScreenHeight;
        this.x = -1;
        this.widthMultiplier = width / (this.y1 - this.y2);
        this.heightMultiplier = height / (this.z1 - this.z2);
    }
    
}
function radians(degrees: number): number {
    return degrees * Math.PI / 180;
}

function rgbToCSS(rgb: number[]): string {
    return "rgb(" + rgb[0] + "," + rgb[1] + "," + rgb[2] + ")";
}