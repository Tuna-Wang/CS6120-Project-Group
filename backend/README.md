# CS6120-Project-Group
## Backend data pipeline
### data_parser
This would process the initial script into a csv that in this format:

|  order_index  | speaker  | text  |
|  ----  | ----  |----  |
| 10  | Humphrey |"What happened? Bernard?"|
| 27 | Jim |"Well..." |

### DB_creator
#### Vector Database
1. character database  
This worker creates vector database for each character that appeared in the script (this should modified if we decide that we only need 'Humphrey'), for now we can imitate all character in the script.
2. personal database  
A personal vector database will be created if a file is detected at the personal_data_path.

#### Retrievers
A character_retriever is created based on the character selected, if no input is received, then the defualt character is set to Humphrey. If a personal vector database is created succesfully then a personal retriever is also created.

### Inmitation
This contains two workers, general and personal:  
The general worker deals with when personal data is not provided, the personal worker deals with when we received personal data, it receives one extra personal retriever compared to the general worker.

## How to run the backend

```bash
pip install -r requirements.txt
```
sometimes you also need to install accelerate  

To run the backend:  
```bash
python3 main.py
```

When the backend is running, you can use POSTMAN to send a request with http://localhost:8000/api/imitate/  
The format of the request could be something like this:  
{
    "text": "What should I do on Monday?",
    "character": "Humphrey",
    "api_key": your_genmini_api_key (gemini_2.0_flash)
}


