import httpx

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

