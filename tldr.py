#take in filename, summarize contents at varying levels of length
#file i/o + api
import os
import anthropic

client = anthropic.Anthropic()

filepath = input("======FILE ANALYZER======\nHello user! Please input the path to the file that you'd like summarized (PDF only):")
length = input("What length would you like the summary to be (small/medium/large)?: ")
complexity = input("And how complex should the response be (simple/medium/advanced)?: ")

#upload the file
upload_response = client.beta.files.upload(
    file=("document.pdf", open(filepath, "rb"), "application/pdf"),
)

file_id = upload_response.id

#response = client.beta.messages.create(
with client.beta.messages.stream(
    model = "claude-sonnet-4-5",
    max_tokens=1024,
    system="You are, as usual, a friendly and helpful assistant. You will be summarizing a given file. Your text will be printed directly to the CLI, so don't bother with markup or formatting.",
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"Write a summary of length {length} of the attached document, at a {complexity} level of complexity:" 
                    #we're assuming claude can handle bad inputs -- it's smart
                },
                {
                    "type": "document",
                    "source": {
                        "type": "file",
                        "file_id": file_id
                    }
                }
            ]
        }
    ],
    betas=["files-api-2025-04-14"],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
#response is full response
#print(response.content[0].text)