class Doc:
    # Inicializa documento com nome, localiza��o e conte�do
    def __init__(self, name, location, content):
        self.name = name
        self.location = location
        self.content = content
        self.embeddings = []
        self.metadata = {}