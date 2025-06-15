class Doc:
    # Inicializa documento com nome, localização e conteúdo
    def __init__(self, name, location, content):
        self.name = name
        self.location = location
        self.content = content
        self.embeddings = []
        self.metadata = {}