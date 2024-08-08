import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from fpdf import FPDF

# Função para carregar dados a partir do upload de arquivos
def load_data():
    base_file = st.file_uploader("Upload base.xlsx", type=["xlsx"])
    retornos_file = st.file_uploader("Upload retornos ativos.xlsx", type=["xlsx"])
    
    if base_file and retornos_file:
        df_base = pd.read_excel(base_file)
        df_retornos = pd.read_excel(retornos_file)
        
        if 'Data de Avaliação' in df_base.columns:
            df_base['Data de Avaliação'] = pd.to_datetime(df_base['Data de Avaliação'], errors='coerce')
        if 'Data de Avaliação' in df_retornos.columns:
            df_retornos['Data de Avaliação'] = pd.to_datetime(df_retornos['Data de Avaliação'], errors='coerce')
        
        return df_base, df_retornos
    else:
        return None, None

# Definir uma paleta de cores personalizada (tons de azul e cinza)
custom_palette = ['#003f5c', '#2f4b7c', '#465a7e', '#64799c', '#7e8fb0', '#98a4c3', '#b2b9d6', '#cccccc']

# Função para gerar gráficos de retornos da carteira
def plot_carteira(data, apolice):
    results = {
        'Período': ['Mês', 'Três Meses', 'Desde o Início'],
        'Retorno': [
            data['Resultado - Mês'].values[0],
            data['Resultado - Três Meses'].values[0],
            data['Resultado - Desde o Início'].values[0]
        ]
    }
    results_df = pd.DataFrame(results).sort_values(by='Retorno', ascending=False)
    fig = px.bar(results_df, x='Período', y='Retorno',
                 labels={'Retorno': 'Retorno (%)', 'Período': 'Período'},
                 text=results_df['Retorno'].apply(lambda x: f'{x:.2f}%'),
                 color='Período', color_discrete_sequence=custom_palette)
    fig.update_traces(texttemplate='%{text}', textposition='outside')
    fig.update_layout(
        yaxis=dict(range=[results_df['Retorno'].min() * 1.1, results_df['Retorno'].max() * 1.1]),  # Permite valores negativos
        xaxis=dict(showticklabels=False),  # Remove os rótulos dos eixos X
        title_x=0.5,
        margin=dict(l=10, r=10, t=50, b=10)  # Ajuste das margens
    )
    return fig

# Função para filtrar e agrupar retornos
def filtrar_agrup_retornos(data_ativos, periodo):
    ultima_data = data_ativos['Data de Avaliação'].max()
    if periodo == 'mês':
        data_inicio = ultima_data - pd.DateOffset(months=1)
    elif periodo == 'trimestre':
        data_inicio = ultima_data - pd.DateOffset(months=3)
    else:
        return pd.DataFrame()

    data_filtrada = data_ativos[(data_ativos['Data de Avaliação'] >= data_inicio) & (data_ativos['Data de Avaliação'] <= ultima_data)]
    retornos_agrupados = data_filtrada.groupby('Nome do Ativo')['Retornos'].sum().reset_index()
    return retornos_agrupados.sort_values(by='Retornos', ascending=False)

# Função para gerar gráficos de retornos dos ativos
def plot_retornos_ativos(data_ativos, periodo, apolice):
    retornos_agrupados = filtrar_agrup_retornos(data_ativos, periodo)
    if retornos_agrupados.empty:
        st.warning(f'Nenhum dado encontrado para o período {periodo}')
        return None

    fig = px.bar(retornos_agrupados, x='Nome do Ativo', y='Retornos',
                 labels={'Retornos': 'Retorno (%)', 'Nome do Ativo': 'Ativo'},
                 text=retornos_agrupados['Retornos'].apply(lambda x: f'{x:.2f}%'),
                 color='Nome do Ativo', color_discrete_sequence=custom_palette)
    fig.update_traces(texttemplate='%{text}', textposition='outside')
    fig.update_layout(
        yaxis=dict(range=[retornos_agrupados['Retornos'].min() * 1.1, retornos_agrupados['Retornos'].max() * 1.1]),  # Permite valores negativos
        xaxis=dict(showticklabels=False),  # Remove os rótulos dos eixos X
        title_x=0.5,
        margin=dict(l=10, r=10, t=50, b=10)  # Ajuste das margens
    )
    return fig

# Função para gerar gráficos dos maiores e menores retornos
def plot_maiores_menores_retornos(data_ativos, periodo, top_n=5):
    retornos_agrupados = filtrar_agrup_retornos(data_ativos, periodo)
    if retornos_agrupados.empty:
        st.warning(f'Nenhum dado encontrado para o período {periodo}')
        return None, None

    sorted_data = retornos_agrupados.sort_values(by='Retornos', ascending=False)
    maiores = sorted_data.head(top_n)
    menores = sorted_data.tail(top_n)

    fig_maiores = px.bar(maiores, x='Nome do Ativo', y='Retornos',
                         labels={'Retornos': 'Retorno (%)', 'Nome do Ativo': 'Ativo'},
                         text=maiores['Retornos'].apply(lambda x: f'{x:.2f}%'),
                         color='Nome do Ativo', color_discrete_sequence=custom_palette)
    fig_maiores.update_traces(texttemplate='%{text}', textposition='outside')
    fig_maiores.update_layout(
        yaxis=dict(range=[maiores['Retornos'].min() * 1.1, maiores['Retornos'].max() * 1.1]),  # Permite valores negativos
        xaxis=dict(showticklabels=False),  # Remove os rótulos dos eixos X
        title_x=0.5,
        margin=dict(l=10, r=10, t=50, b=10)  # Ajuste das margens
    )

    fig_menores = px.bar(menores, x='Nome do Ativo', y='Retornos',
                         labels={'Retornos': 'Retorno (%)', 'Nome do Ativo': 'Ativo'},
                         text=menores['Retornos'].apply(lambda x: f'{x:.2f}%'),
                         color='Nome do Ativo', color_discrete_sequence=custom_palette)
    fig_menores.update_traces(texttemplate='%{text}', textposition='outside')
    fig_menores.update_layout(
        yaxis=dict(range=[menores['Retornos'].min() * 1.1, menores['Retornos'].max() * 1.1]),  # Permite valores negativos
        xaxis=dict(showticklabels=False),  # Remove os rótulos dos eixos X
        title_x=0.5,
        margin=dict(l=10, r=10, t=50, b=10)  # Ajuste das margens
    )

    return fig_maiores, fig_menores

# Função para gerar gráficos de barras para a distribuição dos ativos
def plot_distribuicao(filtro_data):
    filtro_data = filtro_data.sort_values(by='Portfólio %', ascending=False)
    fig_classe = px.pie(filtro_data, names='Classe do Ativo', values='Portfólio %',
                        color_discrete_sequence=custom_palette)
    fig_tipo = px.pie(filtro_data, names='Tipo de Ativo', values='Portfólio %',
                      color_discrete_sequence=custom_palette)
    fig_ativo = px.bar(filtro_data, x='Nome do Ativo', y='Portfólio %',
                       labels={'Portfólio %': 'Portfólio (%)', 'Nome do Ativo': 'Ativo'},
                       text=filtro_data['Portfólio %'].apply(lambda x: f'{x:.2f}%'),
                       color='Nome do Ativo', color_discrete_sequence=custom_palette)
    fig_ativo.update_traces(texttemplate='%{text}', textposition='outside')
    fig_ativo.update_layout(
        yaxis=dict(range=[filtro_data['Portfólio %'].min() * 1.1, filtro_data['Portfólio %'].max() * 1.1]),
        xaxis=dict(showticklabels=False),
        title_x=0.5,
        margin=dict(l=10, r=10, t=50, b=10)
    )
    return fig_classe, fig_tipo, fig_ativo

# Função para salvar gráfico como imagem
def save_plot_as_image(fig, filename):
    fig.write_image(filename)

# Função para gerar um PDF a partir das imagens dos gráficos
def export_pdf(images, output_path, title, resumo):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Adicionar título e resumo
    pdf.add_page()
    pdf.set_font("Arial", 'B', size=18)
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    for key, value in resumo.items():
        pdf.cell(200, 10, txt=f"{key}: {value}", ln=True, align='L')
    pdf.ln(10)

    # Adicionar gráficos em quadrantes
    for i in range(0, len(images), 2):
        pdf.add_page()
        for j in range(2):
            if i + j < len(images):
                x = 10 if j % 2 == 0 else 105
                y = 30
                pdf.image(images[i + j], x=x, y=y, w=90, h=100)

    pdf.output(output_path)

def main():
    # Carregar os dados
    df_base, df_retornos = load_data()

    if df_base is not None and df_retornos is not None:
        if 'Data de Avaliação' in df_retornos.columns:
            ultima_data = df_retornos['Data de Avaliação'].max()
            mes_recente = ultima_data.strftime('%B')
            meses_pt = {
                "January": "Janeiro", "February": "Fevereiro", "March": "Março", "April": "Abril",
                "May": "Maio", "June": "Junho", "July": "Julho", "August": "Agosto",
                "September": "Setembro", "October": "Outubro", "November": "Novembro", "December": "Dezembro"
            }
            mes_recente_pt = meses_pt[mes_recente]
        else:
            st.error('A coluna "Data de Avaliação" não foi encontrada no DataFrame de retornos.')
            return

        st.title(f'Estratégia Internacional - {mes_recente_pt}')
        st.markdown("""
            Bem-vindo ao painel de análise de investimentos. Utilize a barra lateral para navegar entre diferentes seções.
        """)
        st.markdown("---")

        apolice = st.selectbox('Selecione o Número da Apólice', df_base['Número da Apólice'].unique())

        data_base = df_base[df_base['Número da Apólice'] == apolice]
        data_retornos = df_retornos[df_retornos['Número da Apólice'] == apolice]

        valor_conta_recente = data_retornos[data_retornos['Data de Avaliação'] == ultima_data]['Valor de Conta'].values[0]

        st.write("### Resumo da Apólice Selecionada")
        df_resumo = pd.DataFrame({
            'Número da Apólice': apolice,
            'Nome(s) do(s) Participante(s) do Plano': data_retornos['Nome(s) do(s) Participante(s) do Plano'].unique(),
            'Valor de Conta': [f"${valor_conta_recente:,.2f}"],
            'Mês da Apuração': [mes_recente_pt]
        })
        st.write(df_resumo)

        resumo_info = {
            "Número da Apólice": apolice,
            "Nome(s) do(s) Participante(s) do Plano": ', '.join(data_retornos['Nome(s) do(s) Participante(s) do Plano'].unique()),
            "Valor de Conta": f"${valor_conta_recente:,.2f}",
            "Mês da Apuração": mes_recente_pt
        }

        images = []

        st.header('Retornos da Carteira')

        if all(col in data_base.columns for col in ['Resultado - Mês', 'Resultado - Três Meses', 'Resultado - Desde o Início']):
            fig_carteira = plot_carteira(data_base, apolice)
            st.plotly_chart(fig_carteira, use_container_width=True)
            temp_img_path = f"temp_carteira_{apolice}.png"
            save_plot_as_image(fig_carteira, temp_img_path)
            images.append(temp_img_path)
        else:
            st.error('As colunas necessárias para calcular os retornos da carteira não foram encontradas.')

        st.subheader('Retornos dos Ativos - Trimestre')
        fig_trimestre = plot_retornos_ativos(data_retornos, 'trimestre', apolice)
        if fig_trimestre:
            st.plotly_chart(fig_trimestre, use_container_width=True)
            temp_img_path = f"temp_trimestre_{apolice}.png"
            save_plot_as_image(fig_trimestre, temp_img_path)
            images.append(temp_img_path)
        
        st.subheader('Retornos dos Ativos - Mês')
        fig_mes = plot_retornos_ativos(data_retornos, 'mês', apolice)
        if fig_mes:
            st.plotly_chart(fig_mes, use_container_width=True)
            temp_img_path = f"temp_mes_{apolice}.png"
            save_plot_as_image(fig_mes, temp_img_path)
            images.append(temp_img_path)

        st.subheader('Maiores e Menores Retornos - Trimestre')
        fig_maiores_trimestre, fig_menores_trimestre = plot_maiores_menores_retornos(data_retornos, 'trimestre')
        if fig_maiores_trimestre and fig_menores_trimestre:
            st.plotly_chart(fig_maiores_trimestre, use_container_width=True)
            st.plotly_chart(fig_menores_trimestre, use_container_width=True)
            temp_img_path_maiores = f"temp_maiores_trimestre_{apolice}.png"
            temp_img_path_menores = f"temp_menores_trimestre_{apolice}.png"
            save_plot_as_image(fig_maiores_trimestre, temp_img_path_maiores)
            save_plot_as_image(fig_menores_trimestre, temp_img_path_menores)
            images.append(temp_img_path_maiores)
            images.append(temp_img_path_menores)

        st.subheader('Maiores e Menores Retornos - Mês')
        fig_maiores_mes, fig_menores_mes = plot_maiores_menores_retornos(data_retornos, 'mês')
        if fig_maiores_mes and fig_menores_mes:
            st.plotly_chart(fig_maiores_mes, use_container_width=True)
            st.plotly_chart(fig_menores_mes, use_container_width=True)
            temp_img_path_maiores = f"temp_maiores_mes_{apolice}.png"
            temp_img_path_menores = f"temp_menores_mes_{apolice}.png"
            save_plot_as_image(fig_maiores_mes, temp_img_path_maiores)
            save_plot_as_image(fig_menores_mes, temp_img_path_menores)
            images.append(temp_img_path_maiores)
            images.append(temp_img_path_menores)

        st.header('Distribuição dos Ativos')

        filtro_data = data_retornos[data_retornos['Data de Avaliação'] == ultima_data]

        st.subheader('Distribuição por Classe do Ativo')
        fig_classe, fig_tipo, fig_ativo = plot_distribuicao(filtro_data)
        st.plotly_chart(fig_classe, use_container_width=True)
        temp_img_path = "temp_classe.png"
        save_plot_as_image(fig_classe, temp_img_path)
        images.append(temp_img_path)
        
        st.subheader('Distribuição por Tipo de Ativo')
        st.plotly_chart(fig_tipo, use_container_width=True)
        temp_img_path = "temp_tipo.png"
        save_plot_as_image(fig_tipo, temp_img_path)
        images.append(temp_img_path)
        
        st.subheader('Distribuição por Ativo')
        st.plotly_chart(fig_ativo, use_container_width=True)
        temp_img_path = "temp_ativo.png"
        save_plot_as_image(fig_ativo, temp_img_path)
        images.append(temp_img_path)

        if st.button("Exportar para PDF"):
            output_pdf = "relatorio_investimentos.pdf"
            export_pdf(images, output_pdf, f"Estratégia Internacional - {mes_recente_pt}", resumo_info)
            
            with open(output_pdf, "rb") as pdf_file:
                st.download_button(label="Download PDF", data=pdf_file, file_name="relatorio_investimentos.pdf", mime="application/pdf")

        st.markdown("---")
        st.write("Desenvolvido por Pedro Martins")

if __name__ == "__main__":
    main()
