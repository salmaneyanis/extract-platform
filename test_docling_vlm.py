#!/usr/bin/env python3
"""
Script de test ISOLÉ — à lancer sur le serveur GPU AVANT de déployer le projet.

But : vérifier que Docling + Nanonets-OCR2-3B se chargent et extraient une page
sur ton L4 (CUDA 13), SANS toucher au reste du projet.

Usage :
    # Dans un venv sur le serveur (ou le conteneur extract une fois buildé)
    pip install docling accelerate
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cu130
    python test_docling_vlm.py /chemin/vers/un.pdf

Si ce script marche, le déploiement complet marchera. S'il échoue, on corrige
ICI avant de casser quoi que ce soit.
"""

import sys
import time


def test_vlm(pdf_path: str):
    print("=== Test Docling VLM (Nanonets-OCR2-3B) ===")
    import torch
    print(f"CUDA disponible : {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU : {torch.cuda.get_device_name(0)}")

    from docling.datamodel.base_models import InputFormat
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.pipeline_options import VlmPipelineOptions
    from docling.pipeline.vlm_pipeline import VlmPipeline
    from docling.datamodel.pipeline_options_vlm_model import (
        InlineVlmOptions, InferenceFramework, TransformersModelType, ResponseFormat,
    )
    from docling.datamodel.accelerator_options import AcceleratorDevice

    print("Configuration du VlmPipeline...")
    vlm_options = VlmPipelineOptions(
        vlm_options=InlineVlmOptions(
            repo_id="nanonets/Nanonets-OCR2-3B",
            prompt="Convert this page to markdown. Do not miss any text and only output the bare markdown.",
            response_format=ResponseFormat.MARKDOWN,
            inference_framework=InferenceFramework.TRANSFORMERS,
            transformers_model_type=TransformersModelType.AUTOMODEL_IMAGETEXTTOTEXT,
            supported_devices=[AcceleratorDevice.CUDA, AcceleratorDevice.CPU],
            scale=2.0,
            temperature=0.0,
            max_new_tokens=4096,
        ),
    )

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_cls=VlmPipeline,
                pipeline_options=vlm_options,
            ),
        }
    )

    print(f"Extraction de {pdf_path} (1re fois = chargement du modèle, soyez patient)...")
    start = time.time()
    result = converter.convert(source=pdf_path)
    md = result.document.export_to_markdown()
    elapsed = time.time() - start

    print(f"\n=== OK en {elapsed:.1f}s ===")
    print("--- Premières lignes du markdown ---")
    print("\n".join(md.splitlines()[:30]))
    print("...")
    if torch.cuda.is_available():
        print(f"\nVRAM allouée : {torch.cuda.memory_allocated()/1e9:.2f} Go")


def test_classic(pdf_path: str):
    print("\n=== Test Docling classique (OCR + TableFormer) ===")
    from docling.datamodel.base_models import InputFormat
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
    from docling.datamodel.accelerator_options import AcceleratorOptions, AcceleratorDevice

    opts = PdfPipelineOptions()
    opts.do_ocr = True
    opts.do_table_structure = True
    opts.table_structure_options.mode = TableFormerMode.FAST
    opts.accelerator_options = AcceleratorOptions(device=AcceleratorDevice.AUTO)

    converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)}
    )
    start = time.time()
    result = converter.convert(source=pdf_path)
    md = result.document.export_to_markdown()
    print(f"OK en {time.time()-start:.1f}s, {len(md)} caractères")
    print("\n".join(md.splitlines()[:15]))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_docling_vlm.py /chemin/vers/un.pdf")
        sys.exit(1)
    pdf = sys.argv[1]
    test_vlm(pdf)
    # Décommenter pour tester aussi le mode classique :
    # test_classic(pdf)
