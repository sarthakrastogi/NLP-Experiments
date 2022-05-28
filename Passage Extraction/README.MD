# Task

Write an algorithm to do so (PSEUDOCODE would do)

Based on the above algorithm, write a neat code to extract the contributing statements from a paper. You can use the trial data here: https://ncg-task.github.io/data.html 

Generate an abstractive summary from the extracted contributing statements of the paper (taking the abstract of the paper as the reference summary)

Evaluate your summary against the abstract of the paper using ROUGE-1, ROUGE-2, ROUGE-L, and BERTScore

Store the output from 2,3,4 in a CSV file.

Write about the choice of your summarization algorithm and what advantages and disadvantages in the output “contributing summary” you can make out. How would you overcome the limitations of your algorithm?

# Solution

I decided that extracting the contributions can be framed as a question answering problem. But if I implement a knowledge extraction based approach, it will train the model to generate contribution sentences instead of simply extracting the relevant ones from the text, which is what we want here. So instead I'll try a less conventional approach, passage retrieval. I'm assuming that the contributions are written in the Introduction section only, since this has been the case in most papers I've read.
 
Here's the algorithm for retrieving the paragraphs: https://www.linkedin.com/posts/sarthakrastogi_nlp-deeplearning-machinelearning-activity-6935576218058514432-e1d3 The query is simply set as contributions of this paper.

The remaining tasks are in the Colab notebook below. Please turn on the GPU before executing the code. Since there is a very small amount of data present (fewer than 50 papers were there in the zip file on the site), I've accomplished all tasks using pre-trained transformer models. I fetched and preprocessed the data files locally, and in the notebook I directly fetch them from my github.

I found it more convenient to extract the text of entire papers from the files in each section that end with "Grobid-out.txt". I extract the abstract, title and introduction from each text file and store them in data.csv.
As mentioned in the algorithm in my LinkedIn post, I extract the embeddings for each sentence in the introduction and match them against the embedding of the query using cosine similarity. The 5 most similar sentences are saved as contributions.
I summarise them using another transformer model, and calculate the required metrics.

Here's the Colab notebook: https://drive.google.com/file/d/1smqbZDV5B4Hl6ubR7JKlAlKBkY4niEXU/view?usp=sharing
