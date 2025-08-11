{ pkgs }: {
  deps = [
    pkgs.tesseract
    pkgs.tesseract-ocr.tessdata
    # Bạn có thể giữ lại các package khác đã có sẵn ở đây
  ];
}