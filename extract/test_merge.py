from app.services.docling_service import merge_options, build_pipeline_options_ocr
from app.schemas.extract_schemas import ExtractProfile

# Test : créer les options Docling depuis un profil
config = merge_options(ExtractProfile.BALANCED)
pipeline_options = build_pipeline_options_ocr(config)

print("=== pipeline_options ===")
print(f"do_ocr: {pipeline_options.do_ocr}")
print(f"OCR lang: {pipeline_options.ocr_options.lang}")
print(f"OCR force_full: {pipeline_options.ocr_options.force_full_page_ocr}")
print(f"device: {pipeline_options.accelerator_options.device}")
print(f"do_tables: {pipeline_options.do_table_structure}")
print(f"table_mode: {pipeline_options.table_structure_options.mode}")
print(f"images_scale: {pipeline_options.images_scale}")