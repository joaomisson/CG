# SCC0650 - Computação Gráfica (2023): Trabalho 2

João Antônio Misson Milhorim - 11834331
Reynaldo Coronatto Neto - 12547594

## Requisitos

É necessário utilizar Python3 na versão 3.8 e ter instalado as bibliotecas presentes no arquivo requirements.txt para executar o código.

É recomendado criar um enviroment em Conda para rodar o programa. Para criar o enviroment certifique-se que você tenha Conda instalado em sua máquina. Rode então o seguinte comando para criar o enviroment:

```bash
conda create -n [Env name] python=3.8
```

Em seguida, entre no enviroment criado com o seguinte comando:

```bash
conda activate [Env name]
```

Por fim faça a instalação das bibliotecas necessárias rodando o seguinte comando:

```bash
pip install -r requirements.txt
```

## Execução

Para executar o código, basta ter os requisitos e executar o comando:

```bash
python3 Main.py
```

## Organização

O Projeto foi divido nos seguintes arquivos:

- Main: código principal, execução da lógica da cena
- GLWrapper: classe para instânciar o OpenGL, faz todas as configurações necessárias
- Objects: dicionário python que contém as informações de todos os objetos
- Model: classe para um modelo, cria e lida com todas as funções relacionadas a um objeto
- Objs: pasta com os arquivos .obj e suas texturas

## Comandos

- Mouse - Muda o ponto de referência da câmera
- W - Move a câmera para frente em relação ao ponto de referência
- A - Move a câmera para a esquerda em relação ao ponto de referência
- S - Move a câmera para a trás em relação ao ponto de referência
- D - Move a câmera para a direita em relação ao ponto de referência
- I - Ativa e desativa modo poligonal
- Seta para cima - Move a câmera para cima
- Seta para baixo - Move a câmera para baixo
- U - Reduz a luz ambiente
- P - Aumenta a luz ambiente