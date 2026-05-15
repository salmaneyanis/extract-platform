import asyncio
from app.services.file_services import save_file, get_file, delete_file, Category

# Test save
result = asyncio.run(save_file(b"test data", "test.txt", Category.DOCUMENTS, "text/plain", "doc1"))
print(result)

# Test get
file_path = asyncio.run(get_file("DOCUMENTS/doc1/test.txt"))
print(file_path)

# Test delete
asyncio.run(delete_file("DOCUMENTS/doc1/test.txt"))
