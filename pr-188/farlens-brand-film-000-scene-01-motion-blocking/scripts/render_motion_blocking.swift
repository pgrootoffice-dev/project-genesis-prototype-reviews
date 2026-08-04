#!/usr/bin/env swift

import AppKit
import CoreGraphics
import Foundation

let canvasWidth = 1280
let canvasHeight = 720
let fps = 30
let duration = 10.0

guard CommandLine.arguments.count == 3 else {
    fputs("usage: render_motion_blocking.swift SOURCE_PNG OUTPUT_DIR\n", stderr)
    exit(2)
}

let sourcePath = CommandLine.arguments[1]
let outputDirectory = URL(fileURLWithPath: CommandLine.arguments[2], isDirectory: true)
try FileManager.default.createDirectory(at: outputDirectory, withIntermediateDirectories: true)

guard let sourceImage = NSImage(contentsOfFile: sourcePath),
      let sourceCG = sourceImage.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
    fputs("cannot load source image: \(sourcePath)\n", stderr)
    exit(2)
}

struct BeatFrame {
    let sourceRect: CGRect
    let start: Double
}

// Exact pixel regions from the adopted 1536×1024 Static Sequence sheet.
// x=68 begins to the right of the review-only 01–05 plates. No pixel is
// painted over or regenerated; the labels are excluded by deterministic crop.
let frames: [BeatFrame] = [
    BeatFrame(sourceRect: CGRect(x: 68, y: 60, width: 586, height: 190), start: 0.0),
    BeatFrame(sourceRect: CGRect(x: 68, y: 260, width: 586, height: 184), start: 1.6),
    BeatFrame(sourceRect: CGRect(x: 68, y: 454, width: 586, height: 185), start: 3.0),
    BeatFrame(sourceRect: CGRect(x: 68, y: 648, width: 586, height: 164), start: 5.3),
    BeatFrame(sourceRect: CGRect(x: 68, y: 821, width: 586, height: 161), start: 7.6),
]

let colorSpace = CGColorSpaceCreateDeviceRGB()
let bitmapInfo = CGImageAlphaInfo.premultipliedLast.rawValue
let canvasRect = CGRect(x: 0, y: 0, width: canvasWidth, height: canvasHeight)

func clamp(_ value: Double, _ low: Double = 0.0, _ high: Double = 1.0) -> Double {
    min(high, max(low, value))
}

func smooth(_ value: Double) -> Double {
    let x = clamp(value)
    return x * x * (3.0 - 2.0 * x)
}

func eased(_ value: Double) -> Double {
    let x = clamp(value)
    return x < 0.5 ? 4.0 * x * x * x : 1.0 - pow(-2.0 * x + 2.0, 3.0) / 2.0
}

func crop(_ index: Int) -> CGImage {
    guard let image = sourceCG.cropping(to: frames[index].sourceRect) else {
        fatalError("source crop failed for state \(index + 1)")
    }
    return image
}

let croppedFrames = (0..<frames.count).map(crop)

func heroRect(for image: CGImage) -> CGRect {
    let width = CGFloat(canvasWidth)
    let height = width * CGFloat(image.height) / CGFloat(image.width)
    return CGRect(x: 0,
                  y: (CGFloat(canvasHeight) - height) / 2.0,
                  width: width,
                  height: height)
}

func aspectFillRect(for image: CGImage, horizontalShift: CGFloat = 0) -> CGRect {
    let scale = max(CGFloat(canvasWidth) / CGFloat(image.width),
                    CGFloat(canvasHeight) / CGFloat(image.height))
    let width = CGFloat(image.width) * scale
    let height = CGFloat(image.height) * scale
    return CGRect(x: (CGFloat(canvasWidth) - width) / 2.0 + horizontalShift,
                  y: (CGFloat(canvasHeight) - height) / 2.0,
                  width: width,
                  height: height)
}

func makeHeroMask(for image: CGImage) -> CGImage {
    let graySpace = CGColorSpaceCreateDeviceGray()
    guard let maskContext = CGContext(data: nil, width: canvasWidth, height: canvasHeight,
                                      bitsPerComponent: 8, bytesPerRow: canvasWidth,
                                      space: graySpace,
                                      bitmapInfo: CGImageAlphaInfo.none.rawValue) else {
        fatalError("cannot create hero feather mask")
    }
    maskContext.setFillColor(CGColor(gray: 0.0, alpha: 1.0))
    maskContext.fill(canvasRect)
    let hero = heroRect(for: image)
    let colors = [
        CGColor(gray: 0.0, alpha: 1.0),
        CGColor(gray: 1.0, alpha: 1.0),
        CGColor(gray: 1.0, alpha: 1.0),
        CGColor(gray: 0.0, alpha: 1.0),
    ] as CFArray
    guard let gradient = CGGradient(colorsSpace: graySpace, colors: colors,
                                    locations: [0.0, 0.12, 0.88, 1.0]) else {
        fatalError("cannot create hero feather gradient")
    }
    maskContext.saveGState()
    maskContext.clip(to: hero)
    maskContext.drawLinearGradient(gradient,
                                   start: CGPoint(x: 640, y: hero.minY),
                                   end: CGPoint(x: 640, y: hero.maxY), options: [])
    maskContext.restoreGState()
    guard let mask = maskContext.makeImage() else { fatalError("cannot export hero mask") }
    return mask
}

let heroMasks = croppedFrames.map(makeHeroMask)

func drawImage(_ context: CGContext, _ image: CGImage, in rect: CGRect, alpha: CGFloat = 1.0) {
    context.saveGState()
    context.interpolationQuality = .high
    context.setAlpha(alpha)
    context.draw(image, in: rect)
    context.restoreGState()
}

func drawWorldState(_ context: CGContext, index: Int, time: Double) {
    let image = croppedFrames[index]
    let heldTime = index == 4 ? min(time, 9.30) : time
    let breath = CGFloat((sin(heldTime * 0.42 + Double(index) * 0.7) + 1.0) / 2.0)
    let hero = heroRect(for: image)

    // A subdued enlargement of the same state supplies the 16:9 extension.
    // The ratio-preserved hero is feathered into it, avoiding bars and seams.
    let drift = CGFloat(sin(heldTime * 0.38 + Double(index) * 0.6)) * 1.8
    drawImage(context, image, in: aspectFillRect(for: image, horizontalShift: drift), alpha: 0.56)
    context.setFillColor(CGColor(red: 0.010, green: 0.040, blue: 0.095,
                                 alpha: 0.27 + breath * 0.018))
    context.fill(canvasRect)

    context.saveGState()
    context.clip(to: canvasRect, mask: heroMasks[index])
    drawImage(context, image, in: hero)
    context.restoreGState()
}

func warmColor(_ alpha: CGFloat) -> CGColor {
    CGColor(red: 1.0, green: 0.68, blue: 0.23, alpha: alpha)
}

func drawAmbientBreath(_ context: CGContext, time: Double, strength: CGFloat) {
    let pulse = CGFloat((sin(time * 1.55) + 1.0) / 2.0)
    let colors = [
        CGColor(red: 0.12, green: 0.42, blue: 0.62, alpha: strength * (0.018 + 0.025 * pulse)),
        CGColor(red: 0.02, green: 0.07, blue: 0.16, alpha: 0.0),
    ] as CFArray
    guard let gradient = CGGradient(colorsSpace: colorSpace, colors: colors, locations: [0, 1]) else { return }
    context.drawRadialGradient(
        gradient,
        startCenter: CGPoint(x: 640, y: 355),
        startRadius: 0,
        endCenter: CGPoint(x: 640, y: 355),
        endRadius: 390,
        options: []
    )
}

func drawGlow(_ context: CGContext, center: CGPoint, radius: CGFloat, alpha: CGFloat) {
    let colors = [warmColor(alpha), warmColor(0.0)] as CFArray
    guard let gradient = CGGradient(colorsSpace: colorSpace, colors: colors, locations: [0, 1]) else { return }
    context.drawRadialGradient(gradient, startCenter: center, startRadius: 0,
                               endCenter: center, endRadius: radius, options: [])
}

func drawCurve(_ context: CGContext, from: CGPoint, c1: CGPoint, c2: CGPoint, to: CGPoint,
               progress: Double, width: CGFloat, alpha: CGFloat, phase: CGFloat = 0) {
    let visible = clamp(progress)
    if visible <= 0.0 || alpha <= 0.0 { return }
    let path = CGMutablePath()
    path.move(to: from)
    path.addCurve(to: to, control1: c1, control2: c2)
    context.saveGState()
    context.addPath(path)
    context.setStrokeColor(warmColor(alpha))
    context.setLineWidth(width)
    context.setLineCap(.round)
    context.setLineDash(phase: phase, lengths: [CGFloat(1600 * visible), 2000])
    context.strokePath()
    context.restoreGState()
}

func makeArrivalMask(progress: Double, originX: CGFloat, seed: Double) -> CGImage {
    let p = CGFloat(eased(progress))
    let maximumReach = max(originX, CGFloat(canvasWidth) - originX) + 170
    let reach = p * maximumReach
    let feather: CGFloat = 120
    var pixels = [UInt8](repeating: 0, count: canvasWidth * canvasHeight)

    for y in 0..<canvasHeight {
        let verticalDistance = abs(CGFloat(y) - CGFloat(canvasHeight) * 0.5) / (CGFloat(canvasHeight) * 0.5)
        let shapeScale = 0.90 + verticalDistance * 0.13
        let wave = CGFloat(sin(Double(y) * 0.021 + seed) * 34.0
                         + sin(Double(y) * 0.057 + seed * 1.7) * 11.0)
        for x in 0..<canvasWidth {
            let distance = abs(CGFloat(x) - originX) * shapeScale
            let normalized = (reach + wave - distance + feather) / (feather * 2.0)
            let alpha = smooth(Double(normalized))
            pixels[y * canvasWidth + x] = UInt8(clamp(alpha) * 255.0)
        }
    }

    let graySpace = CGColorSpaceCreateDeviceGray()
    return pixels.withUnsafeMutableBytes { buffer in
        guard let maskContext = CGContext(data: buffer.baseAddress,
                                          width: canvasWidth, height: canvasHeight,
                                          bitsPerComponent: 8, bytesPerRow: canvasWidth,
                                          space: graySpace,
                                          bitmapInfo: CGImageAlphaInfo.none.rawValue),
              let mask = maskContext.makeImage() else {
            fatalError("cannot create organic arrival mask")
        }
        return mask
    }
}

func drawLayerArrival(_ context: CGContext, from: Int, to: Int, progress: Double, time: Double) {
    let p = clamp(progress)
    if p >= 0.999 {
        drawWorldState(context, index: to, time: time)
        return
    }

    drawWorldState(context, index: from, time: time)
    if p <= 0.0 { return }

    let originX: CGFloat = from == 0 ? 585 : 635
    let mask = makeArrivalMask(progress: p, originX: originX,
                               seed: Double(from + 1) * 1.37)
    context.saveGState()
    context.clip(to: canvasRect, mask: mask)
    drawWorldState(context, index: to, time: time)
    context.restoreGState()
}

func drawGatheringLight(_ context: CGContext, time: Double) {
    let p = eased((time - 1.00) / 0.60)
    let held = CGFloat(smooth((time - 1.08) / 0.52))
    drawCurve(context, from: CGPoint(x: 270, y: 360), c1: CGPoint(x: 390, y: 345),
              c2: CGPoint(x: 500, y: 375), to: CGPoint(x: 585, y: 360),
              progress: p, width: 1.4, alpha: 0.13)
    drawCurve(context, from: CGPoint(x: 890, y: 350), c1: CGPoint(x: 760, y: 370),
              c2: CGPoint(x: 670, y: 345), to: CGPoint(x: 585, y: 360),
              progress: p, width: 1.2, alpha: 0.11)
    drawGlow(context, center: CGPoint(x: 585, y: 360), radius: 50 + held * 38,
             alpha: 0.045 + held * 0.085)
}

func drawBirthResponse(_ context: CGContext, time: Double) {
    let p = CGFloat(smooth((time - 1.60) / 0.95))
    drawGlow(context, center: CGPoint(x: 585, y: 360), radius: 70 + p * 65,
             alpha: 0.07 + p * 0.10)
}

func drawPropagation(_ context: CGContext, time: Double, alphaScale: CGFloat = 1.0) {
    let p1 = eased((time - 2.72) / 1.38)
    let p2 = eased((time - 3.08) / 1.35)
    let p3 = eased((time - 3.46) / 1.18)
    drawCurve(context, from: CGPoint(x: 585, y: 360), c1: CGPoint(x: 480, y: 330),
              c2: CGPoint(x: 330, y: 400), to: CGPoint(x: 145, y: 328),
              progress: p1, width: 3.0, alpha: 0.42 * alphaScale)
    drawCurve(context, from: CGPoint(x: 585, y: 360), c1: CGPoint(x: 705, y: 300),
              c2: CGPoint(x: 825, y: 395), to: CGPoint(x: 1085, y: 330),
              progress: p2, width: 2.8, alpha: 0.38 * alphaScale)
    drawCurve(context, from: CGPoint(x: 585, y: 365), c1: CGPoint(x: 640, y: 430),
              c2: CGPoint(x: 760, y: 435), to: CGPoint(x: 925, y: 400),
              progress: p3, width: 2.2, alpha: 0.31 * alphaScale)
}

func drawInteraction(_ context: CGContext, time: Double) {
    let carry = CGFloat(1.0 - 0.48 * smooth((time - 5.85) / 1.15))
    drawPropagation(context, time: 5.30, alphaScale: carry)

    let p1 = eased((time - 5.52) / 1.32)
    let p2 = eased((time - 5.98) / 1.00)
    drawCurve(context, from: CGPoint(x: 145, y: 328), c1: CGPoint(x: 360, y: 300),
              c2: CGPoint(x: 725, y: 420), to: CGPoint(x: 1085, y: 330),
              progress: p1, width: 3.6, alpha: 0.43)
    drawCurve(context, from: CGPoint(x: 1085, y: 330), c1: CGPoint(x: 845, y: 430),
              c2: CGPoint(x: 495, y: 285), to: CGPoint(x: 145, y: 328),
              progress: p2, width: 3.1, alpha: 0.39)

    let response = CGFloat(smooth((time - 6.05) / 0.72))
    drawGlow(context, center: CGPoint(x: 635, y: 360), radius: 105,
             alpha: response * 0.18)
    drawGlow(context, center: CGPoint(x: 860, y: 352), radius: 68,
             alpha: response * 0.09)
}

func drawWorldOpening(_ context: CGContext, time: Double) {
    let heldTime = min(time, 9.30)
    let p = eased((heldTime - 7.72) / 1.42)
    let strength = CGFloat(p)

    drawCurve(context, from: CGPoint(x: 635, y: 360), c1: CGPoint(x: 520, y: 350),
              c2: CGPoint(x: 340, y: 390), to: CGPoint(x: 70, y: 365),
              progress: p, width: 2.4, alpha: 0.22)
    drawCurve(context, from: CGPoint(x: 635, y: 360), c1: CGPoint(x: 760, y: 350),
              c2: CGPoint(x: 925, y: 390), to: CGPoint(x: 1210, y: 365),
              progress: p, width: 2.4, alpha: 0.20)
    drawGlow(context, center: CGPoint(x: 635, y: 360), radius: 140 + strength * 175,
             alpha: 0.055 + strength * 0.075)
}

func render(time: Double, context: CGContext) {
    context.setFillColor(CGColor(red: 0.018, green: 0.060, blue: 0.130, alpha: 1.0))
    context.fill(canvasRect)

    if time < 1.60 {
        drawWorldState(context, index: 0, time: time)
        drawAmbientBreath(context, time: time, strength: 1.0)
        if time >= 1.00 { drawGatheringLight(context, time: time) }
    } else if time < 3.00 {
        drawLayerArrival(context, from: 0, to: 1,
                         progress: (time - 1.60) / 1.02, time: time)
        drawBirthResponse(context, time: time)
    } else if time < 5.30 {
        drawLayerArrival(context, from: 1, to: 2,
                         progress: (time - 3.00) / 1.18, time: time)
        drawPropagation(context, time: time)
    } else if time < 7.60 {
        drawLayerArrival(context, from: 2, to: 3,
                         progress: (time - 5.30) / 1.18, time: time)
        drawInteraction(context, time: time)
    } else {
        drawLayerArrival(context, from: 3, to: 4,
                         progress: (time - 7.60) / 1.32, time: time)
        drawWorldOpening(context, time: time)
    }
}

for outputIndex in 0..<Int(duration * Double(fps)) {
    autoreleasepool {
        guard let context = CGContext(data: nil,
                                      width: canvasWidth,
                                      height: canvasHeight,
                                      bitsPerComponent: 8,
                                      bytesPerRow: canvasWidth * 4,
                                      space: colorSpace,
                                      bitmapInfo: bitmapInfo) else {
            fatalError("cannot create frame context")
        }
        render(time: Double(outputIndex) / Double(fps), context: context)
        guard let output = context.makeImage() else { fatalError("cannot create frame image") }
        let bitmap = NSBitmapImageRep(cgImage: output)
        guard let png = bitmap.representation(using: .png, properties: [:]) else {
            fatalError("cannot encode frame")
        }
        let name = String(format: "frame-%04d.png", outputIndex)
        try! png.write(to: outputDirectory.appendingPathComponent(name), options: .atomic)
    }
}

print("rendered \(Int(duration * Double(fps))) frames")
