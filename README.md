# AdsSearchBackend
Ads recommender system 

# How to run
<p>pip install virtualenv</p>
<p>python -m venv env</p>
<p>For Linux: source env/bin/activate</p>
<p>For Windows: .\env\Scripts\activate</p>
<p>pip install -r requirements.txt</p>

# Common Errors
<h3>NLTK error</h3>
<p>nltk.download('stopwords', download_dir='E:/div_code/django_env/nltk_data')</p>

<p>import nltk
stopwords = nltk.corpus.stopwords.words('english')
print(stopwords[:10])</p>