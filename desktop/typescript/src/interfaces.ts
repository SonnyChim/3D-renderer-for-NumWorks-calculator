interface IRenderer {
    height: number;
    width: number;
}

interface ITri3d {
    x1: number;
    y1: number;
    z1: number;
    x2: number;
    y2: number;
    z2: number;
    x3: number;
    y3: number;
    z3: number;
    project(screen: IProjectionScreen): Tri2d | undefined;
}

interface IProjectionScreen {
    y1: number;
    z1: number;
    y2: number;
    z2: number;
    x: number;
    widthMultiplier: number;
    heightMultiplier: number;
    setFOV(fov: number, height: number, width: number): void;
}

interface IPosition {
    offsetCache: Offset;
    clearcache(): void;
    getOffset(): Offset;
};

interface IFileHandler {
    loadFile(): Promise<[string, string]>;
    parseFile(): []
}

interface IScene {

}