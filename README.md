## Background
The intent of this project was to provide EvaDB with the ability to answer questions based on information from a Git repository. The reference repository for this project was AI For Beginners by Microsoft (https://github.com/microsoft/AI-For-Beginners), however, there are a number of similar repositories with interactive lessons. Being able to use these as references to answer questions would be very useful.

Additionally, a similar technique could be used with code repositories. A developer could ask a question about the architecture of a codebase, and by referencing the code, the comments, and the documentation in a repository, the LLM could answer the question. This would be invaluable for onboarding new developers onto a project, among a variety of other tasks.

## Implementation
The implementation is broken down into two phases. For this project, the unique piece is extending EvaDB to be able to load a repository. To do this, once the function has been imported, the user should run it with a cursor to an existing database and a repository URL:

load_repository(cursor, "https://github.com/microsoft/AI-For-Beginners.git")

The implementation does a few things. First, it clones the repository. Next, it goes through all the files, loading the text files into the database. As a part of this, it also extracts the text from the .ipynb files, as many repositories make their content interactive through python notebooks, but this format is not very conducive for LLMs. 

From here, a user lean on EvaDB’s built in ChatGPT support to ask a question with the repository as context, as seen in the following command:

SELECT ChatGPT('What is this lesson about?', text) 
FROM repository 
WHERE name = 'lessons/5-NLP/16-RNN/RNNPyTorch.ipynb'

The corresponding output is:

“This lesson is about recurrent neural networks (RNNs) and their applications in natural language processing tasks. It covers the basics of RNNs, including how they capture the order of words in a sequence, and introduces two popular types of RNN architectures: simple RNN and Long Short Term Memory (LSTM). The lesson also discusses the challenges of training RNNs and introduces the concept of packed sequences to handle variable-length input. Additionally, it explores bidirectional and multilayer RNNs and mentions that RNNs can be used for tasks beyond sequence classification, such as text generation and machine translation.”

This makes it very easy to ask questions that have contextual information from a repository. Additionally, built in features of EvaDB can be leveraged, such as the ability to ask questions regarding multiple rows:

SELECT ChatGPT('What is this lesson about?', text)
FROM repository LIMIT 10

In a single SQL query, EvaDB can answer the same question about multiple files in a repository. This example also showcases the benefits of EvaDB’s optimizer. Running the query on a single row takes approximately 13 seconds. However, the second example running the query over 10 rows takes approximately 70 seconds, which is not a linear increase in time. Instead of having to manually batch and optimize the query, the user can write simple SQL queries and let EvaDB figure out the best way to execute it.

## Lessons and challenges
LLM APIs have a per query token limit. This poses a challenge when trying to query a repository with many files. Therefore, it is currently not possible to ask a question generically over the entire text in a repository. Instead, as implemented currently, the file which will most likely contain the desired context has to be manually selected by the user, which puts some limitations on the usability of the integration. However, the integration is still useful for many use cases. For example, with the reference AI for Beginners repository, all the content relating to a specific ML framework is contained within a single file.

Additionally, EvaDB’s AI functions are not really the right place to implement a repository loader. Ideally, the query language itself would have been extended, allowing for a statement such as LOAD REPOSITORY instead of a separate python function, making it easier to use and more aligned with the rest of EvaDB. However, I had some trouble getting this to work.

## Future improvements
The biggest improvement for this integration would be the ability for a single question to reference the full contents of the repository. There are multiple potential options for this. First, it may be possible to simply use a local LLM, such as the open Llama 2 model from Meta to work around token length restrictions. A more performant alternative would be to compile the repository to vector embeddings and use them as context for the question. 

It would also be useful for the user experience to integrate repository loading into the EvaDB query language. 

### References
The EvaDB Documentation (https://evadb.readthedocs.io/en/latest/index.html#)
The EvaDB Repository (https://github.com/georgia-tech-db/evadb)
CS-4420 Piazza
ChatGPT for help with Python
