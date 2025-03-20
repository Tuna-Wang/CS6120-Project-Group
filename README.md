# CS6120-Project-Group
## ➡️ 1 Objective
This is an end to end project of a chatbot with configurable conversational styles. By default the chatbot adopts the conversational style of the beloved character from Yes, Minister -- Humphrey Appleby.

## ➡️ 2 Motivation
### ❓ What are you trying to do?
Build a chatbot that can imitate the tone of a person. This person can be anyone, depending on the provided dataset.
### ❓ How is it done today, and what are the limits of current practice? 
⚠️ < literature review here>  
For personalizing LLM, Salemi and Zamani (2024) categorized the current approaches in two main approaches, Retrieval-augmented generation (RAG) and parameter-efficient fine-tuning (PEFT). They conducted experiments to evaluate the two approaches and found that RAG performs better.    
Muhammad (2024) used an approach where after collecting written samples of the target author that he wanted to imitate, chunked the dataset into manageable parts, then he used LLMs to generate questions for the chunked part. Then he used these question-answer pairs to fine-tune the model. This is an efficient way of fine-tuning a model and preserve the writing style, but this method might struggle when dealing with questions that are out-of-scope of the original dataset provided.  
< to be continued ...>
### ❓ How we proposed to improve it?
⚠️ < some day dreams here>
### ❓ Who cares?
This chatbot may be useful under these scenarios:  
1. Recreation of a beloved one: This chatbot can converse with users in the style of their favored ones. For example, the current training dataset is the script of 'Yes, Minister,' a 1980s sitcom that has been off the air for many years, with many of its actors having passed away and no new episodes being produced. Although there are no new episodes, we can use the script to train the chatbot and have a virtual assistant like Sir Humphrey Appleby, the capable Permanent Secretary, to help us solve problems, bring joy to our lives.  This allow us to bring our favorite characters to life, keeping them with us forever.  
2. Literature review helper: The current LLMs are very good at summarizing and paraphrasing. However, it does not know of the writting style of each individual user, thus it cannot provide summarization in our words, with our writting style. With the user's previous work, this chatbot can create more authentic writtings.
## ➡️ 3 Background
Under the research topic of authorship attribution, forensic linguists have explored qualitative and quantitative methods to analyze whether a text or passage is from the same author. This inspired us to propose a project to "reverse engineer" the process of authorship attribution. We are committed to combining linguistics and NLP, using linguitcs approach to retrieve linguistic features from training datasets, and with the help of RAG technology, we can train information retrieval models to enable LLMs to output the style we want to imitate.  
⚠️ < more specific forensic science work should be referenced>   
⚠️ < more techinical approaches should be specified>
## ➡️ 4 Proposed Approach
⚠️ < Scale of data > the current dataset, the ideal size of dataset to train new customized models.  
⚠️ < Noise >  
⚠️ < Algorithms >   
⚠️ < Preprocessing >  
⚠️ < Class imbalance >  
Evaluation: Both qualitative and quantitative methods used in analyzing authorship attribution; Our feelings.

### References
Muhammad, H. (2024, May 5). Finetune LLM to imitate the writing style of someone. Medium. https://medium.com/@m.hayyan32/imitate-writing-style-with-llm-b6862cd699e7  
Salemi, A., & Zamani, H. (2024). Comparing retrieval-augmentation and parameter-efficient fine-tuning for privacy-preserving personalization of large language models. arXiv preprint arXiv:2409.09510. https://arxiv.org/abs/2409.09510
