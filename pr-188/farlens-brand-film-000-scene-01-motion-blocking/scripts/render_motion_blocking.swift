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
    let label: String
}

// Pixel coordinates in the adopted 1536x1024 Static Sequence sheet. The number
// plate and the approved frame artwork remain untouched inside each crop.
let frames: [BeatFrame] = [
    BeatFrame(sourceRect: CGRect(x: 24, y: 60, width: 630, height: 190), start: 0.0, label: "Frame 1 / Beat 1"),
    BeatFrame(sourceRect: CGRect(x: 24, y: 260, width: 630, height: 184), start: 1.6, label: "Frame 2 / Beat 2"),
    BeatFrame(sourceRect: CGRect(x: 24, y: 454, width: 630, height: 185), start: 3.0, label: "Frame 3 / Beat 3"),
    BeatFrame(sourceRect: CGRect(x: 24, y: 648, width: 630, height: 164), start: 5.3, label: "Frame 4 / Beat 3→4"),
    BeatFrame(sourceRect: CGRect(x: 24, y: 821, width: 630, height: 161), start: 7.6, label: "Frame 5 / Beat 4"),
]

let colorSpace = CGColorSpaceCreateDeviceRGB()
let bitmapInfo = CGImageAlphaInfo.premultipliedLast.rawValue

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
    // CGImage crop coordinates have their origin at the top-left.
    guard let image = sourceCG.cropping(to: frames[index].sourceRect) else {
        fatalError("source crop failed for frame \(index + 1)")
    }
    return image
}

let croppedFrames = (0..<frames.count).map(crop)

func contentRect(for image: CGImage, scaleMultiplier: CGFloat = 1.0) -> CGRect {
    let safe = CGRect(x: 0, y: 66, width: canvasWidth, height: canvasHeight - 132)
    let scale = min(safe.width / CGFloat(image.width), safe.height / CGFloat(image.height)) * scaleMultiplier
    let width = CGFloat(image.width) * scale
    let height = CGFloat(image.height) * scale
    return CGRect(x: (CGFloat(canvasWidth) - width) / 2.0,
                  y: (CGFloat(canvasHeight) - height) / 2.0,
                  width: width,
                  height: height)
}

func drawImage(_ context: CGContext, _ image: CGImage, scale: CGFloat = 1.0) {
    context.saveGState()
    context.interpolationQuality = .high
    context.draw(image, in: contentRect(for: image, scaleMultiplier: scale))
    context.restoreGState()
}

func warmColor(_ alpha: CGFloat) -> CGColor {
    CGColor(red: 1.0, green: 0.68, blue: 0.23, alpha: alpha)
}

func blueColor(_ alpha: CGFloat) -> CGColor {
    CGColor(red: 0.16, green: 0.55, blue: 0.82, alpha: alpha)
}

func drawAmbientBreath(_ context: CGContext, time: Double, strength: CGFloat) {
    let pulse = CGFloat((sin(time * 1.7) + 1.0) / 2.0)
    let center = CGPoint(x: 640, y: 335)
    let colors = [
        CGColor(red: 0.12, green: 0.42, blue: 0.62, alpha: strength * (0.02 + 0.035 * pulse)),
        CGColor(red: 0.02, green: 0.07, blue: 0.16, alpha: 0.0),
    ] as CFArray
    guard let gradient = CGGradient(colorsSpace: colorSpace, colors: colors, locations: [0, 1]) else { return }
    context.drawRadialGradient(gradient, startCenter: center, startRadius: 0, endCenter: center, endRadius: 360, options: [])
}

func drawGlow(_ context: CGContext, center: CGPoint, radius: CGFloat, alpha: CGFloat) {
    let colors = [warmColor(alpha), warmColor(0.0)] as CFArray
    guard let gradient = CGGradient(colorsSpace: colorSpace, colors: colors, locations: [0, 1]) else { return }
    context.drawRadialGradient(gradient, startCenter: center, startRadius: 0, endCenter: center, endRadius: radius, options: [])
}

func drawCurve(_ context: CGContext, from: CGPoint, c1: CGPoint, c2: CGPoint, to: CGPoint,
               progress: Double, width: CGFloat, alpha: CGFloat, phase: CGFloat = 0) {
    let path = CGMutablePath()
    path.move(to: from)
    path.addCurve(to: to, control1: c1, control2: c2)
    context.saveGState()
    context.addPath(path)
    context.setStrokeColor(warmColor(alpha))
    context.setLineWidth(width)
    context.setLineCap(.round)
    // Every registered curve is shorter than 1,600px. Growing one long dash
    // makes the visible stroke travel all the way to its semantic destination.
    context.setLineDash(phase: phase, lengths: [CGFloat(1600 * clamp(progress)), 2000])
    context.strokePath()
    context.restoreGState()
}

func drawFrame2Reveal(_ context: CGContext, time: Double) {
    drawImage(context, croppedFrames[0])
    let p = eased((time - 1.60) / 0.70)
    let center = CGPoint(x: 572, y: 352)
    context.saveGState()
    context.addEllipse(in: CGRect(x: center.x - CGFloat(p) * 920,
                                  y: center.y - CGFloat(p) * 620,
                                  width: CGFloat(p) * 1840,
                                  height: CGFloat(p) * 1240))
    context.clip()
    drawImage(context, croppedFrames[1])
    context.restoreGState()
    if time > 1.72 {
        let local = smooth((time - 1.72) / 0.8)
        drawGlow(context, center: CGPoint(x: 590, y: 354), radius: 105 + CGFloat(local) * 42, alpha: 0.12 + CGFloat(local) * 0.08)
    }
}

func drawFrame3Reveal(_ context: CGContext, time: Double) {
    drawImage(context, croppedFrames[1])
    let base = (time - 3.00) / 0.90
    let regions: [(CGPoint, Double)] = [
        (CGPoint(x: 570, y: 360), 0.00),
        (CGPoint(x: 300, y: 365), 0.16),
        (CGPoint(x: 865, y: 350), 0.32),
    ]
    for (center, delay) in regions {
        let p = eased((base - delay) / (1.0 - delay))
        context.saveGState()
        let radius = CGFloat(p) * 900
        context.addEllipse(in: CGRect(x: center.x - radius, y: center.y - radius * 0.62,
                                      width: radius * 2, height: radius * 1.24))
        context.clip()
        drawImage(context, croppedFrames[2])
        context.restoreGState()
    }
}

func drawPropagation(_ context: CGContext, time: Double) {
    let p1 = eased((time - 3.18) / 1.25)
    let p2 = eased((time - 3.55) / 1.25)
    let p3 = eased((time - 3.88) / 1.05)
    drawCurve(context, from: CGPoint(x: 565, y: 360), c1: CGPoint(x: 480, y: 335),
              c2: CGPoint(x: 340, y: 390), to: CGPoint(x: 160, y: 325),
              progress: p1, width: 3.2, alpha: 0.45)
    drawCurve(context, from: CGPoint(x: 570, y: 360), c1: CGPoint(x: 690, y: 305),
              c2: CGPoint(x: 815, y: 390), to: CGPoint(x: 1035, y: 330),
              progress: p2, width: 3.0, alpha: 0.40)
    drawCurve(context, from: CGPoint(x: 570, y: 365), c1: CGPoint(x: 630, y: 425),
              c2: CGPoint(x: 750, y: 430), to: CGPoint(x: 900, y: 400),
              progress: p3, width: 2.4, alpha: 0.34)
}

func drawFrame4Reveal(_ context: CGContext, time: Double) {
    drawImage(context, croppedFrames[2])
    let starts: [(CGPoint, Double)] = [
        (CGPoint(x: 295, y: 360), 5.30),
        (CGPoint(x: 640, y: 345), 5.45),
        (CGPoint(x: 965, y: 350), 5.60),
    ]
    for (center, start) in starts {
        let p = eased((time - start) / 0.80)
        let radius = CGFloat(p) * 780
        context.saveGState()
        context.addEllipse(in: CGRect(x: center.x - radius, y: center.y - radius * 0.55,
                                      width: radius * 2, height: radius * 1.10))
        context.clip()
        drawImage(context, croppedFrames[3])
        context.restoreGState()
    }
}

func drawInteraction(_ context: CGContext, time: Double) {
    let p = eased((time - 5.55) / 1.35)
    let accelerated = eased((time - 6.15) / 0.9)
    drawCurve(context, from: CGPoint(x: 130, y: 378), c1: CGPoint(x: 365, y: 305),
              c2: CGPoint(x: 650, y: 415), to: CGPoint(x: 1125, y: 330),
              progress: p, width: 3.8, alpha: 0.45)
    drawCurve(context, from: CGPoint(x: 220, y: 320), c1: CGPoint(x: 445, y: 430),
              c2: CGPoint(x: 720, y: 285), to: CGPoint(x: 1060, y: 395),
              progress: accelerated, width: 3.2, alpha: 0.42)
    let crossingAlpha = CGFloat(smooth((time - 6.0) / 0.8)) * 0.24
    drawGlow(context, center: CGPoint(x: 642, y: 360), radius: 110, alpha: crossingAlpha)
    drawGlow(context, center: CGPoint(x: 872, y: 350), radius: 75, alpha: crossingAlpha * 0.7)
}

func drawFrame5Reveal(_ context: CGContext, time: Double) {
    drawImage(context, croppedFrames[3])
    let p = eased((time - 7.60) / 0.75)
    context.saveGState()
    let width = CGFloat(p) * 1500
    let height = CGFloat(p) * 820
    context.addEllipse(in: CGRect(x: 640 - width / 2, y: 360 - height / 2, width: width, height: height))
    context.clip()
    drawImage(context, croppedFrames[4])
    context.restoreGState()
}

func drawWorldOpening(_ context: CGContext, time: Double) {
    let p = eased((time - 7.75) / 1.35)
    let settle = 1.0 - smooth((time - 9.20) / 0.45)
    let strength = CGFloat(p * settle)
    drawGlow(context, center: CGPoint(x: 640, y: 360), radius: 160 + strength * 260, alpha: 0.15 * strength)
    drawCurve(context, from: CGPoint(x: 160, y: 390), c1: CGPoint(x: 390, y: 345),
              c2: CGPoint(x: 520, y: 360), to: CGPoint(x: 640, y: 360),
              progress: p, width: 2.6, alpha: 0.24 * strength)
    drawCurve(context, from: CGPoint(x: 1120, y: 390), c1: CGPoint(x: 900, y: 345),
              c2: CGPoint(x: 760, y: 360), to: CGPoint(x: 640, y: 360),
              progress: p, width: 2.6, alpha: 0.22 * strength)
}

func render(time: Double, context: CGContext) {
    context.setFillColor(CGColor(red: 0.012, green: 0.035, blue: 0.082, alpha: 1.0))
    context.fill(CGRect(x: 0, y: 0, width: canvasWidth, height: canvasHeight))

    if time < 1.6 {
        drawImage(context, croppedFrames[0])
        drawAmbientBreath(context, time: time, strength: 1.0)
    } else if time < 3.0 {
        drawFrame2Reveal(context, time: time)
    } else if time < 5.3 {
        if time < 3.95 { drawFrame3Reveal(context, time: time) } else { drawImage(context, croppedFrames[2]) }
        drawPropagation(context, time: time)
    } else if time < 7.6 {
        if time < 6.45 { drawFrame4Reveal(context, time: time) } else { drawImage(context, croppedFrames[3]) }
        drawInteraction(context, time: time)
    } else {
        if time < 8.40 { drawFrame5Reveal(context, time: time) } else { drawImage(context, croppedFrames[4]) }
        drawWorldOpening(context, time: time)
    }
}

for frameNumber in 0..<Int(duration * Double(fps)) {
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
        // The bitmap context and CGImage crop already share the orientation needed by
        // the exported PNG. Do not add a second vertical transform here.
        render(time: Double(frameNumber) / Double(fps), context: context)
        guard let output = context.makeImage() else { fatalError("cannot create frame image") }
        let bitmap = NSBitmapImageRep(cgImage: output)
        guard let png = bitmap.representation(using: .png, properties: [:]) else {
            fatalError("cannot encode frame")
        }
        let name = String(format: "frame-%04d.png", frameNumber)
        try! png.write(to: outputDirectory.appendingPathComponent(name), options: .atomic)
    }
}

print("rendered \(Int(duration * Double(fps))) frames")
