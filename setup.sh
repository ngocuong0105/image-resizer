mkdir -p ~/.streamlit/

echo "
[server]\n
headless = true\n
port = $PORT\n
enableCORS = false\n
[theme]
base = 'light'\n
primaryColor = '#ffcc2a'\n
backgroundColor = '#f8f4d5'\n
\n
" > ~/.streamlit/config.toml
