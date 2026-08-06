#!/usr/bin/env swift

import AppKit
import CoreGraphics
import Foundation

let canvasWidth = 1280
let canvasHeight = 720
let fps = 30
let duration = 13.0
let frameCount = Int(duration * Double(fps))
let canvasRect = CGRect(x: 0, y: 0, width: canvasWidth, height: canvasHeight)

guard CommandLine.arguments.count == 7 else {
    fputs("usage: render_motion_blocking.swift A1.png A2.png A3.png A4.png A5.png OUTPUT_DIR\n", stderr)
    exit(2)
}

let sourcePaths = Array(CommandLine.arguments[1...5])
let outputDirectory = URL(fileURLWithPath: CommandLine.arguments[6], isDirectory: true)
try FileManager.default.createDirectory(at: outputDirectory, withIntermediateDirectories: true)

let sourceImages: [CGImage] = sourcePaths.map { path in
    guard let image = NSImage(contentsOfFile: path),
          let cgImage = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
        fputs("cannot load adopted Static image: \(path)\n", stderr)
        exit(2)
    }
    return cgImage
}

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

func drawImage(_ context: CGContext, _ image: CGImage, alpha: CGFloat = 1.0,
               offset: CGPoint = .zero, scale: CGFloat = 1.0) {
    let width = CGFloat(canvasWidth) * scale
    let height = CGFloat(canvasHeight) * scale
    let rect = CGRect(x: (CGFloat(canvasWidth) - width) / 2.0 + offset.x,
                      y: (CGFloat(canvasHeight) - height) / 2.0 + offset.y,
                      width: width, height: height)
    context.saveGState()
    context.interpolationQuality = .high
    context.setAlpha(alpha)
    context.draw(image, in: rect)
    context.restoreGState()
}

func makeBandMask(slot: Int) -> CGImage {
    struct Band { let x0, x1, center, amplitude, thickness, phase: CGFloat }
    let bands: [Band] = [
        Band(x0: -80, x1: 650, center: 570, amplitude: 52, thickness: 112, phase: 0.1),
        Band(x0: 70, x1: 760, center: 480, amplitude: 45, thickness: 96, phase: 1.2),
        Band(x0: 360, x1: 1030, center: 575, amplitude: 42, thickness: 104, phase: 2.3),
        Band(x0: 330, x1: 1110, center: 440, amplitude: 47, thickness: 94, phase: 0.7),
        Band(x0: 590, x1: 1320, center: 535, amplitude: 42, thickness: 100, phase: 1.7),
        Band(x0: 690, x1: 1360, center: 405, amplitude: 40, thickness: 90, phase: 2.8),
        Band(x0: 170, x1: 950, center: 365, amplitude: 35, thickness: 82, phase: 1.0),
        Band(x0: 540, x1: 1300, center: 335, amplitude: 31, thickness: 76, phase: 2.1),
    ]
    let band = bands[slot]
    guard let context = CGContext(data: nil, width: canvasWidth, height: canvasHeight,
                                  bitsPerComponent: 8, bytesPerRow: canvasWidth,
                                  space: CGColorSpaceCreateDeviceGray(),
                                  bitmapInfo: CGImageAlphaInfo.none.rawValue) else {
        fatalError("cannot create membrane mask")
    }
    context.setFillColor(CGColor(gray: 0, alpha: 1))
    context.fill(canvasRect)
    let path = CGMutablePath()
    let samples = 64
    for index in 0...samples {
        let q = CGFloat(index) / CGFloat(samples)
        let x = band.x0 + (band.x1 - band.x0) * q
        let y = band.center + sin(q * .pi * 2.0 + band.phase) * band.amplitude + band.thickness / 2.0
        index == 0 ? path.move(to: CGPoint(x: x, y: y)) : path.addLine(to: CGPoint(x: x, y: y))
    }
    for index in stride(from: samples, through: 0, by: -1) {
        let q = CGFloat(index) / CGFloat(samples)
        let x = band.x0 + (band.x1 - band.x0) * q
        let y = band.center + sin(q * .pi * 2.0 + band.phase) * band.amplitude - band.thickness / 2.0
        path.addLine(to: CGPoint(x: x, y: y))
    }
    path.closeSubpath()
    context.setFillColor(CGColor(gray: 1, alpha: 1))
    context.addPath(path)
    context.fillPath()
    guard let image = context.makeImage() else { fatalError("cannot export membrane mask") }
    return image
}

let membraneMasks = (0..<8).map(makeBandMask)

func makeFocusMask() -> CGImage {
    guard let context = CGContext(data: nil, width: canvasWidth, height: canvasHeight,
                                  bitsPerComponent: 8, bytesPerRow: canvasWidth,
                                  space: CGColorSpaceCreateDeviceGray(),
                                  bitmapInfo: CGImageAlphaInfo.none.rawValue) else {
        fatalError("cannot create parent-child focus mask")
    }
    context.setFillColor(CGColor(gray: 0, alpha: 1))
    context.fill(canvasRect)
    let colors = [CGColor(gray: 1, alpha: 1), CGColor(gray: 0, alpha: 1)] as CFArray
    guard let gradient = CGGradient(colorsSpace: CGColorSpaceCreateDeviceGray(), colors: colors,
                                    locations: [0.68, 1.0]) else { fatalError("focus gradient") }
    context.drawRadialGradient(gradient,
                               startCenter: CGPoint(x: 244, y: 145), startRadius: 30,
                               endCenter: CGPoint(x: 244, y: 145), endRadius: 360,
                               options: [])
    guard let image = context.makeImage() else { fatalError("cannot export focus mask") }
    return image
}

func makeBackgroundBlurMask() -> CGImage {
    guard let context = CGContext(data: nil, width: canvasWidth, height: canvasHeight,
                                  bitsPerComponent: 8, bytesPerRow: canvasWidth,
                                  space: CGColorSpaceCreateDeviceGray(),
                                  bitmapInfo: CGImageAlphaInfo.none.rawValue) else {
        fatalError("cannot create background blur mask")
    }
    let colors = [CGColor(gray: 0, alpha: 1), CGColor(gray: 1, alpha: 1)] as CFArray
    guard let gradient = CGGradient(colorsSpace: CGColorSpaceCreateDeviceGray(), colors: colors,
                                    locations: [0.65, 1.0]) else { fatalError("background blur gradient") }
    context.drawRadialGradient(gradient,
                               startCenter: CGPoint(x: 244, y: 145), startRadius: 25,
                               endCenter: CGPoint(x: 244, y: 145), endRadius: 370,
                               options: [.drawsAfterEndLocation])
    guard let image = context.makeImage() else { fatalError("cannot export background blur mask") }
    return image
}

func makeSkyRestoreMask() -> CGImage {
    guard let context = CGContext(data: nil, width: canvasWidth, height: canvasHeight,
                                  bitsPerComponent: 8, bytesPerRow: canvasWidth,
                                  space: CGColorSpaceCreateDeviceGray(),
                                  bitmapInfo: CGImageAlphaInfo.none.rawValue) else {
        fatalError("cannot create sky restore mask")
    }
    let colors = [CGColor(gray: 0, alpha: 1), CGColor(gray: 0, alpha: 1),
                  CGColor(gray: 1, alpha: 1), CGColor(gray: 1, alpha: 1)] as CFArray
    guard let gradient = CGGradient(colorsSpace: CGColorSpaceCreateDeviceGray(), colors: colors,
                                    locations: [0.0, 0.27, 0.40, 1.0]) else {
        fatalError("sky restore gradient")
    }
    context.drawLinearGradient(gradient, start: CGPoint(x: 0, y: 0),
                               end: CGPoint(x: 0, y: CGFloat(canvasHeight)), options: [])
    guard let image = context.makeImage() else { fatalError("cannot export sky restore mask") }
    return image
}

let focusMask = makeFocusMask()
let backgroundBlurMask = makeBackgroundBlurMask()
let skyRestoreMask = makeSkyRestoreMask()

func drawClipped(_ context: CGContext, image: CGImage, mask: CGImage, alpha: CGFloat) {
    guard alpha > 0.001 else { return }
    context.saveGState()
    context.clip(to: canvasRect, mask: mask)
    drawImage(context, image, alpha: alpha)
    context.restoreGState()
}

func drawSoftBlur(_ context: CGContext, image: CGImage, alpha: CGFloat, radius: CGFloat) {
    guard alpha > 0.001 else { return }
    let offsets = [
        CGPoint(x: 0, y: 0), CGPoint(x: radius, y: 0), CGPoint(x: -radius, y: 0),
        CGPoint(x: 0, y: radius), CGPoint(x: 0, y: -radius),
        CGPoint(x: radius * 0.7, y: radius * 0.7), CGPoint(x: -radius * 0.7, y: radius * 0.7),
        CGPoint(x: radius * 0.7, y: -radius * 0.7), CGPoint(x: -radius * 0.7, y: -radius * 0.7),
    ]
    for offset in offsets {
        drawImage(context, image, alpha: alpha / CGFloat(offsets.count), offset: offset)
    }
}

func drawAtmosphere(_ context: CGContext, time: Double, strength: CGFloat) {
    let breath = CGFloat((sin(time * 0.72) + 1.0) * 0.5)
    let colors = [
        CGColor(red: 0.12, green: 0.35, blue: 0.50, alpha: strength * (0.012 + breath * 0.018)),
        CGColor(red: 0.01, green: 0.04, blue: 0.10, alpha: 0),
    ] as CFArray
    guard let gradient = CGGradient(colorsSpace: colorSpace, colors: colors, locations: [0, 1]) else { return }
    context.drawRadialGradient(gradient, startCenter: CGPoint(x: 700, y: 350), startRadius: 0,
                               endCenter: CGPoint(x: 700, y: 350), endRadius: 540, options: [])
}

// A stable contrast veil keeps the adopted left-lower terrain masses latent
// through A1-A3 without blur, focus manipulation, movement, or new geometry.
// A4 removes only this priority veil while separating the existing contours.
func drawLatentMassPriorityVeil(_ context: CGContext, strength: CGFloat) {
    guard strength > 0.001 else { return }
    context.saveGState()
    context.clip(to: canvasRect, mask: focusMask)
    context.setFillColor(CGColor(red: 0.015, green: 0.055, blue: 0.12,
                                 alpha: strength * 0.13))
    context.fill(canvasRect)
    context.restoreGState()
}

func drawDistantLightBreath(_ context: CGContext, time: Double, strength: CGFloat) {
    let breath = CGFloat(0.5 + 0.5 * sin(time * 0.86))
    let alpha = strength * (0.012 + breath * 0.018)
    let colors = [CGColor(red: 1.0, green: 0.67, blue: 0.27, alpha: alpha),
                  CGColor(red: 1.0, green: 0.57, blue: 0.18, alpha: 0)] as CFArray
    guard let gradient = CGGradient(colorsSpace: colorSpace, colors: colors, locations: [0, 1]) else { return }
    context.drawRadialGradient(gradient, startCenter: CGPoint(x: 1158, y: 214), startRadius: 0,
                               endCenter: CGPoint(x: 1158, y: 214), endRadius: 24, options: [])
}

func drawA1(_ context: CGContext, time: Double) {
    drawImage(context, sourceImages[0])
    let breath = CGFloat(0.22 + 0.025 * sin(time * 0.8))
    for slot in 0..<3 {
        drawClipped(context, image: sourceImages[1], mask: membraneMasks[slot], alpha: breath)
    }
    drawLatentMassPriorityVeil(context, strength: 1.0)
    drawAtmosphere(context, time: time, strength: 0.65)
}

func drawA2(_ context: CGContext, time: Double) {
    let local = time - 2.2
    let complete = CGFloat(smooth((local - 1.45) / 0.65))
    drawImage(context, sourceImages[0])
    for slot in 0..<3 {
        drawClipped(context, image: sourceImages[1], mask: membraneMasks[slot], alpha: 0.28)
    }
    for slot in 3..<6 {
        let stagger = Double(slot - 3) * 0.18
        let p = CGFloat(eased((local - stagger) / 1.12))
        let depthDrift = CGPoint(x: CGFloat(slot - 4) * p * 1.2, y: p * CGFloat(slot % 2 == 0 ? 1.1 : -0.8))
        context.saveGState()
        context.translateBy(x: depthDrift.x, y: depthDrift.y)
        drawClipped(context, image: sourceImages[1], mask: membraneMasks[slot], alpha: 0.18 + p * 0.62)
        context.restoreGState()
    }
    drawImage(context, sourceImages[1], alpha: complete)
    drawLatentMassPriorityVeil(context, strength: 1.0)
    drawAtmosphere(context, time: time, strength: 0.55)
}

func drawA3(_ context: CGContext, time: Double) {
    let local = time - 4.6
    let fullState = CGFloat(smooth((local - 1.35) / 0.72))
    drawImage(context, sourceImages[1])
    for slot in 0..<6 {
        let p = CGFloat(smooth((local - 0.08) / 1.24))
        drawClipped(context, image: sourceImages[2], mask: membraneMasks[slot], alpha: p * 0.34)
    }
    for slot in 6..<8 {
        let stagger = Double(slot - 6) * 0.26
        let p = CGFloat(eased((local - stagger) / 1.12))
        drawClipped(context, image: sourceImages[2], mask: membraneMasks[slot], alpha: p * 0.82)
    }
    drawImage(context, sourceImages[2], alpha: fullState)
    let refraction = CGFloat(smooth((local - 0.45) / 1.35))
    context.setFillColor(CGColor(red: 0.09, green: 0.25, blue: 0.31, alpha: refraction * 0.035))
    context.fill(CGRect(x: 410, y: 230, width: 650, height: 360))
    drawLatentMassPriorityVeil(context, strength: 1.0)
    drawAtmosphere(context, time: time, strength: 0.42)
}

func drawA4Focused(_ context: CGContext, time: Double, arrival: CGFloat) {
    let sourceMix = 1.0 - arrival
    drawImage(context, sourceImages[2], alpha: sourceMix)
    drawImage(context, sourceImages[3], alpha: arrival)

    let blurStrength = CGFloat(smooth((time - 7.45) / 1.05)) * arrival
    drawLatentMassPriorityVeil(context, strength: 1.0 - arrival)
    if blurStrength > 0.001 {
        context.saveGState()
        context.clip(to: canvasRect, mask: backgroundBlurMask)
        drawSoftBlur(context, image: sourceImages[3], alpha: blurStrength * 0.82, radius: 4.2)
        context.restoreGState()
        context.setFillColor(CGColor(red: 0.015, green: 0.055, blue: 0.12, alpha: blurStrength * 0.055))
        context.fill(CGRect(x: 360, y: 285, width: 920, height: 435))
    }
    let focusArrival = CGFloat(smooth(Double(arrival) / 0.58))
    drawClipped(context, image: sourceImages[3], mask: focusMask, alpha: focusArrival)
    drawAtmosphere(context, time: time, strength: 0.32)
}

func drawA5Clean(_ context: CGContext, time: Double, alpha: CGFloat) {
    guard alpha > 0.001 else { return }
    context.saveGState()
    context.setAlpha(alpha)
    // Composite the complete recovered-world treatment as one transparency
    // group. Nested helpers set their own alpha, so the group preserves the
    // 1.75-second recovery envelope instead of replacing it per draw call.
    context.beginTransparencyLayer(auxiliaryInfo: nil)
    // A5 restores the world outside the fixed Parent/Child focus zone. The
    // source states differ by a few pixels, so excluding that zone prevents
    // a cross-fade from manufacturing a duplicate family silhouette.
    context.clip(to: canvasRect, mask: backgroundBlurMask)
    drawImage(context, sourceImages[4])
    context.saveGState()
    context.clip(to: canvasRect, mask: skyRestoreMask)
    drawImage(context, sourceImages[0])
    context.restoreGState()
    drawAtmosphere(context, time: time, strength: 0.26)
    drawDistantLightBreath(context, time: time, strength: 0.55)
    context.endTransparencyLayer()
    context.restoreGState()
}

func render(time: Double, context: CGContext) {
    context.setFillColor(CGColor(red: 0.008, green: 0.035, blue: 0.083, alpha: 1))
    context.fill(canvasRect)

    if time < 2.2 {
        drawA1(context, time: time)
    } else if time < 4.6 {
        drawA2(context, time: time)
    } else if time < 7.2 {
        drawA3(context, time: time)
    } else if time < 10.0 {
        let arrival = CGFloat(eased((time - 7.2) / 1.45))
        drawA4Focused(context, time: time, arrival: arrival)
    } else {
        let recovery = CGFloat(eased((time - 10.0) / 1.75))
        drawA4Focused(context, time: time, arrival: 1.0)
        drawA5Clean(context, time: time, alpha: recovery)
        // Parent and Child stay on the exact A4 ground contact throughout the
        // recovery. A5 changes the world's readability, not their position.
        drawClipped(context, image: sourceImages[3], mask: focusMask, alpha: 1.0)
    }
}

for index in 0..<frameCount {
    autoreleasepool {
        guard let context = CGContext(data: nil, width: canvasWidth, height: canvasHeight,
                                      bitsPerComponent: 8, bytesPerRow: canvasWidth * 4,
                                      space: colorSpace, bitmapInfo: bitmapInfo) else {
            fatalError("cannot create frame context")
        }
        let time = Double(index) / Double(fps)
        render(time: time, context: context)
        guard let frame = context.makeImage() else { fatalError("cannot export frame") }
        let rep = NSBitmapImageRep(cgImage: frame)
        guard let data = rep.representation(using: .png, properties: [:]) else {
            fatalError("cannot encode frame")
        }
        let url = outputDirectory.appendingPathComponent(String(format: "frame-%04d.png", index + 1))
        try! data.write(to: url)
    }
}

print("Rendered \(frameCount) frames at \(fps)fps / \(duration)s")
