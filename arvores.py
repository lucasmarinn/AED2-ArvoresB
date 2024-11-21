import random
import time
import string
from memory_profiler import profile
import matplotlib.pyplot as plt  # Para gerar os gráficos


# Definindo a classe Produto com categoria
class Produto:
    def __init__(self, produto_id, nome, preco, categoria):
        self.produto_id = produto_id
        self.nome = nome
        self.preco = preco
        self.categoria = categoria

    def __repr__(self):
        return f"Produto(ID={self.produto_id}, Nome={self.nome}, Preço={self.preco:.2f}, Categoria={self.categoria})"

# Árvore B
class BTreeNode:
    def __init__(self, t, is_leaf=True):
        self.t = t
        self.is_leaf = is_leaf
        self.keys = []
        self.children = []

    def split_child(self, i, y):
        t = self.t
        new_node = BTreeNode(t, y.is_leaf)
        self.keys.insert(i, y.keys[t - 1])
        self.children.insert(i + 1, new_node)
        new_node.keys = y.keys[t:]
        y.keys = y.keys[:t - 1]
        if not y.is_leaf:
            new_node.children = y.children[t:]
            y.children = y.children[:t]

class BTree:
    def __init__(self, t):
        self.t = t
        self.root = BTreeNode(t)

    def insert(self, produto):
        root = self.root
        if len(root.keys) == 2 * self.t - 1:
            new_root = BTreeNode(self.t, False)
            new_root.children.append(self.root)
            new_root.split_child(0, self.root)
            self.root = new_root
        self._insert_non_full(self.root, produto)

    def _insert_non_full(self, node, produto):
        i = len(node.keys) - 1
        if node.is_leaf:
            while i >= 0 and produto.produto_id < node.keys[i].produto_id:
                i -= 1
            node.keys.insert(i + 1, produto)
        else:
            while i >= 0 and produto.produto_id < node.keys[i].produto_id:
                i -= 1
            i += 1
            child = node.children[i]
            if len(child.keys) == 2 * self.t - 1:
                node.split_child(i, child)
                if produto.produto_id > node.keys[i].produto_id:
                    i += 1
            self._insert_non_full(node.children[i], produto)

    def search(self, node, produto_id):
        i = 0
        while i < len(node.keys) and produto_id > node.keys[i].produto_id:
            i += 1
        if i < len(node.keys) and produto_id == node.keys[i].produto_id:
            return node.keys[i]
        if node.is_leaf:
            return None
        return self.search(node.children[i], produto_id)

    def traverse(self, node=None, result=None):
        if result is None:
            result = []
        if node is None:
            node = self.root
        for i in range(len(node.keys)):
            if not node.is_leaf:
                self.traverse(node.children[i], result)
            result.append(node.keys[i])
        if not node.is_leaf:
            self.traverse(node.children[len(node.keys)], result)
        return result

# Árvore B+
class BPlusTreeNode:
    def __init__(self, t, is_leaf=False):
        self.t = t
        self.is_leaf = is_leaf
        self.keys = []
        self.children = []
        self.next = None

class BPlusTree:
    def __init__(self, t):
        self.t = t
        self.root = BPlusTreeNode(t, True)

    def insert(self, produto):
        root = self.root
        if len(root.keys) == 2 * self.t - 1:
            new_root = BPlusTreeNode(self.t, False)
            new_root.children.append(self.root)
            self.split_child(new_root, 0)
            self.root = new_root
        self._insert_non_full(self.root, produto)

    def split_child(self, parent, i):
        t = self.t
        child = parent.children[i]
        new_node = BPlusTreeNode(t, child.is_leaf)
        parent.keys.insert(i, child.keys[t - 1])
        parent.children.insert(i + 1, new_node)
        new_node.keys = child.keys[t:]
        child.keys = child.keys[:t - 1]
        if not child.is_leaf:
            new_node.children = child.children[t:]
            child.children = child.children[:t]
        else:
            new_node.next = child.next
            child.next = new_node

    def _insert_non_full(self, node, produto):
        i = len(node.keys) - 1
        if node.is_leaf:
            while i >= 0 and produto.produto_id < node.keys[i].produto_id:
                i -= 1
            node.keys.insert(i + 1, produto)
        else:
            while i >= 0 and produto.produto_id < node.keys[i].produto_id:
                i -= 1
            i += 1
            child = node.children[i]
            if len(child.keys) == 2 * self.t - 1:
                self.split_child(node, i)
                if produto.produto_id > node.keys[i].produto_id:
                    i += 1
            self._insert_non_full(node.children[i], produto)

    def search(self, node, produto_id):
        i = 0
        while i < len(node.keys) and produto_id > node.keys[i].produto_id:
            i += 1
        if i < len(node.keys) and produto_id == node.keys[i].produto_id:
            return node.keys[i]
        if node.is_leaf:
            return None
        return self.search(node.children[i], produto_id)

    def traverse_leaf(self):
        node = self.root
        while not node.is_leaf:
            node = node.children[0]
        count = 0
        while node:
            count += len(node.keys)
            node = node.next
        return count

def criar_produtos(qtd):
    categorias = ["Eletrônicos", "Livros", "Eletrodomésticos", "Moda", "Esportes",
                  "Beleza e Saúde", "Brinquedos", "Automotivo", "Móveis", "Alimentos e Bebidas"]
    produtos = []
    for i in range(qtd):
        produto_id = i + 1
        nome = ''.join(random.choices(string.ascii_uppercase, k=5))
        preco = round(random.uniform(10.0, 500.0), 2)
        categoria = random.choice(categorias)
        produtos.append(Produto(produto_id, nome, preco, categoria))
    return produtos

# Função para testar a performance
def testar_performance(estrutura, qtd_produtos, t=3):
    produtos = criar_produtos(qtd_produtos)

    if estrutura == "BTree":
        tree = BTree(t)
    elif estrutura == "BPlusTree":
        tree = BPlusTree(t)
    else:
        raise ValueError("Estrutura inválida.")

    # Teste de inserção
    start_time = time.time()
    for produto in produtos:
        tree.insert(produto)
    insercao_tempo = time.time() - start_time

    # Teste de busca
    start_time = time.time()
    for produto in produtos:
        tree.search(tree.root, produto.produto_id)
    busca_tempo = time.time() - start_time

    # Teste de travessia
    start_time = time.time()
    if estrutura == "BTree":
        tree.traverse()
    elif estrutura == "BPlusTree":
        tree.traverse_leaf()
    travessia_tempo = time.time() - start_time

    # Retornar tempos como dicionário
    return {
        "insercao": insercao_tempo,
        "busca": busca_tempo,
        "travessia": travessia_tempo
    }



def menu():
    print("\nMenu:")
    print("1. Testar Árvore B")
    print("2. Testar Árvore B+")
    print("3. Sair")


def executar_teste_multiplo(estrutura):
    # Configurações de testes
    quantidades = [10000, 100000, 1000000]
    graus = [2, 3, 5]
    repeticoes = 6

    # Resultados acumulados para cálculo das médias
    resultados = {
        "insercao": [],
        "busca": [],
        "travessia": []
    }

    for qtd in quantidades:
        for t in graus:
            tempos_insercao = []
            tempos_busca = []
            tempos_travessia = []

            for _ in range(repeticoes):
                tempos = testar_performance(estrutura, qtd, t)
                tempos_insercao.append(tempos["insercao"])
                tempos_busca.append(tempos["busca"])
                tempos_travessia.append(tempos["travessia"])

            # Calcular a média dos tempos
            resultados["insercao"].append((qtd, t, sum(tempos_insercao) / repeticoes))
            resultados["busca"].append((qtd, t, sum(tempos_busca) / repeticoes))
            resultados["travessia"].append((qtd, t, sum(tempos_travessia) / repeticoes))

    # Plotar os resultados
    plotar_graficos(resultados, estrutura)

def plotar_graficos(resultados, estrutura):
    for tipo in ["insercao", "busca", "travessia"]:
        plt.figure()
        for qtd, t, tempo in resultados[tipo]:
            plt.scatter(t, tempo, label=f"Produtos: {qtd}")
            plt.plot(t, tempo, marker='o')  # Para conectar os pontos

        plt.title(f"{estrutura} - Desempenho ({tipo})")
        plt.xlabel("Grau da Árvore (t)")
        plt.ylabel("Tempo (s)")
        plt.legend()
        plt.grid(True)
        plt.show()

def main():
    while True:
        menu()
        choice = input("Escolha uma opção: ")
        if choice == "1":
            print("Executando testes para Árvore B...")
            executar_teste_multiplo("BTree")
        elif choice == "2":
            print("Executando testes para Árvore B+...")
            executar_teste_multiplo("BPlusTree")
        elif choice == "3":
            print("Saindo...")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()

