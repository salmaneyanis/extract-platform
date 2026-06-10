import httpx
import time 

async def upload_document(file_content,file_name):
    #envoie le fichier  au store_data pour qu'il le stocke le infos et que que le doc recoive un id
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "http://store_data:3003/documents",
            json={"filename": file_name}
        )
        data = resp.json()
        doc_id = data["doc_id"]


        # ensuite on l'envoie à retrieve pour stocker le fichier dans le volume (l'id qu'aura recu le fichier permettra de le mettre dans un folder avec son id)
        files = {"uploaded_file": (file_name,file_content)}
        data = {"category": "originals", "doc_id": str(doc_id)}
        resp = await client.post(
            "http://retrieve:3002/files",
            files=files,
            data=data
        )

        data = resp.json()
        file_path = data["file_path"]


    return {"doc_id": doc_id, "status": "uploaded", "file_path": file_path}


async def extract_document(file_path,output_format,device):
    #on extract le fichier en fonction de l'id donner
    async with httpx.AsyncClient() as client:
          # 1. GET fichier depuis retrieve
          resp = await client.get(
              f"http://retrieve:3002/files/{file_path}"
          )
          resp.raise_for_status()
          file_content = resp.content

          # 2. POST extract avec fichier
          files = {"file": ("document", file_content)}
          resp = await client.post(
              "http://extract:3001/extract",
              files=files,
              data={
                  "output_format": output_format,
                  "device": device,
              },
          )
          resp.raise_for_status()
          extract_data = resp.json()

    return extract_data

async def save_parse(doc_id, content_markdown, content_json, output_format):
      async with httpx.AsyncClient() as client:
          resp = await client.post(
              "http://store_data:3003/parses",
              json={
                  "doc_id": doc_id,
                  "representation_type": output_format,
                  "content_json": content_json,
                  "content_text": content_markdown,
              }
          )
          resp.raise_for_status()
      return resp.json()

async def create_job(doc_id):
      async with httpx.AsyncClient() as client:
          resp = await client.post(
              "http://store_data:3003/jobs",
              json={
                  "doc_id": doc_id,
                  "job_type": "extract",
              }
          )
          resp.raise_for_status()
      return resp.json()

async def update_job(job_id, status, result=None):
      async with httpx.AsyncClient() as client:
          resp = await client.patch(
              f"http://store_data:3003/jobs/{job_id}",
              json={
                  "status": status,
                  "result": result,
              }
          )
          resp.raise_for_status()
      return resp.json()

async def process_document(
      file_content: bytes,
      file_name: str,
      profile: str = "balanced",
      device: str = "auto",
      output_format: str = "markdown",
  ):
      """Orchestrate: upload → create job → extract → save parse → update job."""
      start_time = time.time()
      doc_id = None
      job_id = None

      try:
          # 1. Upload document
          upload_result = await upload_document(file_content, file_name)
          doc_id = upload_result["doc_id"]
          file_path = upload_result["file_path"]

          # 2. Create job
          job_result = await create_job(doc_id)
          job_id = job_result["job_id"]

          # 3. Extract document
          extract_result = await extract_document(
              file_path, output_format, device
          )

          # 4. Save parse
          parse_result = await save_parse(
              doc_id,
              extract_result.get("content_markdown"),
              extract_result.get("content_json"),
              output_format,
          )

          # 5. Update job status
          await update_job(
              job_id,
              "done",
              {
                  "parse_id": parse_result["parse_id"],
                  "processing_time_ms": (time.time() - start_time) * 1000,
              },
          )

          return {
              "job_id": job_id,
              "doc_id": doc_id,
              "status": "done",
              "processing_time_ms": (time.time() - start_time) * 1000,
          }

      except Exception as e:
          if job_id:
              await update_job(job_id, "failed", {"error": str(e)})
          return {
              "job_id": job_id,
              "doc_id": doc_id,
              "status": "failed",
              "error": str(e),
              "processing_time_ms": (time.time() - start_time) * 1000,
          }