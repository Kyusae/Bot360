from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common import exceptions as ex
import time

Email = str(input('Digite o e-mail a acessar: '))
Senha = str(input('Digite a senha do e-mail: '))
Filial = str(input('Digite o nome da filial: '))
Pedido = str(input('Pedido a ser sincronizado: '))

class Bot360:
    def __init__(self, username, password, filial, Pedido):
        self.username = username
        self.password = password
        self.filial = filial
        self.Pedido = Pedido
        self.driver = webdriver.Firefox(executable_path="geckodriver.exe")

    def login(self):
        driver = self.driver
        driver.get("") #URL
        driver.set_window_size(1882,1096)
        time.sleep(2)
        
        #Login do usuario
        botaoemail = driver.find_element(By.ID, "email")
        botaoemail.click()
        botaoemail.clear()
        botaoemail.send_keys(self.username)

        botaosenha = driver.find_element(By.ID, "password")
        botaosenha.click()
        botaosenha.clear()
        botaosenha.send_keys(self.password)
        botaosenha.send_keys(Keys.RETURN)

        time.sleep(3)

        #Seleciona a filial após o acesso
        try:
            botaoAcesso = driver.find_element(By.ID, 'selectedId')
            botaoAcesso.click()
            botaoAcesso.clear()
            botaoAcesso.send_keys(self.filial)
            botaoAcesso.send_keys(Keys.RETURN)
            time.sleep(3)
            botaoAcesso.send_keys(Keys.RETURN)
        except ex.NoSuchElementException:
            print('Valide os dados de acesso!')

        #Aguarda a tela principal do 360 abrir
        time.sleep(10)

        #Busca o icone da transportadora para entrar na pagina de "Acompanhamento de Pedidos"
        try:
            botaoListagemPedido = driver.find_element(By.XPATH, "//*[local-name()='svg' and @data-icon='car']")
            botaoListagemPedido.click()
            entrarListagemPedido = driver.find_element(By.XPATH, '//a[@href="/carrier/ordertracking"]')
            entrarListagemPedido.click()
        except ex.NoSuchElementException:
            driver.refresh()

        #Aguardar a tela carregar
        time.sleep(5)

        #Busca o filtro
        try:
            botaoFiltroPedido = driver.find_element(By.XPATH, "//*[local-name()='svg' and @data-icon='filter']")
            botaoFiltroPedido.click()
        except ex.NoSuchElementException:
            driver.refresh()

        time.sleep(5)

        #Filtra o pedido
        botaoAcesso = driver.find_element(By.ID, 'orderNumber')
        botaoAcesso.click()
        botaoAcesso.clear()
        botaoAcesso.send_keys(self.Pedido)

        time.sleep(2)

        #Busca o botão "Buscar" para aplicar o filtro
        try:
            ClicaBotaoBuscar = driver.find_element(By.XPATH, '/html/body/div[3]/div/div[2]/div/div/div[2]/div/div/div/div/div/form/div[8]/div/div/span/div/button')
            ClicaBotaoBuscar.click()
        except ex.NoSuchElementException:
            driver.refresh()

        time.sleep(2)

        #Fecha o filtro
        fechaFiltroPedido = driver.find_element(By.XPATH, "//*[local-name()='svg' and @data-icon='close']")
        fechaFiltroPedido.click()

        time.sleep(20)

        #Atualiza a pagina para garantir o pedido no filtro
        driver.refresh()
        
        time.sleep(5)

        #Procura o Status do pedido
        ValidaStatus = driver.find_element(By.XPATH, "/html/body/div[1]/div/section/section/main/div[2]/div/div[3]/div/div/div/div/div/div/div/div/div/div/div/table/tbody/tr[2]/td[9]")
        
        #Valida se o status atual do pedido permite a sincronização, se sim, realiza a sincronização
        if ValidaStatus.text == 'Coletado' or ValidaStatus.text == "Sincronizando com transportadora" or ValidaStatus.text == "Aguardando Coleta":
            print('Pedido com status diferente dos que podem realizar o envio!')
        else:
            while (ValidaStatus.text == "Sincronização pendente" or ValidaStatus.text == "Erro de integração"):
                StatusTransportadoraAntigo = ValidaStatus.text
                print(StatusTransportadoraAntigo + ' - Status Pré Click')
                
                #Procura o botão "Enviar Todos" para sincronizar o pedido
                EnviaPedidoPraTransportadora = driver.find_element(By.XPATH, "/html/body/div[1]/div/section/section/main/div[2]/div/div[2]/div/div/div/div/div[1]/div[2]/button")
                EnviaPedidoPraTransportadora.click()
                
                #Aguarda 5s para que a ação do botão tenha sido concluida
                time.sleep(5)
                #Atualiza a pagina para validar o pedido novamente
                driver.refresh()
                time.sleep(2)
                
                #Procura o novo Status do pedido
                ValidaStatus = driver.find_element(By.XPATH, "/html/body/div[1]/div/section/section/main/div[2]/div/div[3]/div/div/div/div/div/div/div/div/div/div/div/table/tbody/tr[2]/td[9]")
                
                StatusTransportadoraNovo = ValidaStatus.text
                print(StatusTransportadoraNovo + ' - Status Pós Click')
                
                #Em caso de o pedido estar anteriormente em "Sincronização pendente" e for para "Erro de Integração" não faz sentido continuar tentando sincronizar, logo ele para a aplicação 
                if StatusTransportadoraAntigo == "Sincronização pendente" and StatusTransportadoraNovo == "Erro de integração":
                    print('Pedido gerou erro de integração ao sincronizar com a transportadora, verifique os logs!')
                    break
                else:
                    continue
            else:
                if ValidaStatus.text == "Coletado":
                    print('Pedido enviado a transportadora com sucesso!')
                elif ValidaStatus.text == "Sincronizando com transportadora":
                    print('Pedido sincronizando com a transportadora, aguarde!')
                else:
                    print('Erro desconhecido, valide!')

guilhermeBot = Bot360(Email, Senha, Filial, Pedido)
guilhermeBot.login()
