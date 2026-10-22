// Extract a PDF's text layer the way a parser sees it (macOS PDFKit).
// Usage: pdftext <file.pdf>   -> first line "PAGES: n", then the text.
import PDFKit
guard CommandLine.arguments.count > 1,
      let d = PDFDocument(url: URL(fileURLWithPath: CommandLine.arguments[1])) else {
  FileHandle.standardError.write("cannot open PDF\n".data(using: .utf8)!); exit(1)
}
print("PAGES:", d.pageCount)
print(d.string ?? "")
