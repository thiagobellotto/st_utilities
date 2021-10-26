#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import streamlit as st
from streamlit.errors import StreamlitAPIException
import io
import numpy as np
from PIL import Image
import base64

@st.cache(suppress_st_warning=True, allow_output_mutation=True, show_spinner=False)
def reduce_precision(df):
        cols_to_convert = []
        date_strings = ['_date', 'date_', 'date', 'data', 'Data', 'Datas', 'datas', 'Data de cancelamento']

        for col in df.columns:
            col_type = df[col].dtype
            if 'string' not in col_type.name and col_type.name != 'category' and 'datetime' not in col_type.name:
                cols_to_convert.append(col)

        def _reduce_precision(x):
            col_type = x.dtype
            unique_data = list(x.unique())
            bools = [True, False, 'true', 'True', 'False', 'false']
            n_unique = float(len(unique_data))
            n_records = float(len(x))
            cat_ratio = n_unique / n_records

            try:
                unique_data.remove(np.nan)
            except:
                pass

            if 'int' in str(col_type):
                c_min = x.min()
                c_max = x.max()

                if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                    x= x.astype(np.int8)
                elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                    x = x.astype(np.int16)
                elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                    x = x.astype(np.int32)
                elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
                    x = x.astype(np.int64)

                    # TODO: set precision to unsigned integers with nullable NA

            elif 'float' in str(col_type):
                c_min = x.min()
                c_max = x.max()
                if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                        x = x.astype(np.float16)
                elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                    x = x.astype(np.float32)
                else:
                    x = x.astype(np.float64)

            elif 'datetime' in col_type.name or any(i in str(x.name).lower() for i in date_strings):
                try:
                    x = pd.to_datetime(x)
                except:
                    pass

            elif any(i in bools for i in unique_data):
                x = x.astype('boolean')
                #TODO: set precision to bool if boolean not needed

            elif cat_ratio < .1 or n_unique < 20:
                x = x.astype('category')

            elif all(isinstance(i, str) for i in unique_data):
                x = x.astype('string')

            return x

        df[cols_to_convert] = df[cols_to_convert].apply(lambda x: _reduce_precision(x))

        return df

@st.cache(suppress_st_warning=True, allow_output_mutation=True, show_spinner=False)
def reduce_image_size_without_losing_quality(image_path, max_size=8164):
    """
    Reduce the size of an image without losing the image quality.
    """
    image = Image.open(image_path)
    width, height = image.size
    if width <= max_size and height <= max_size:
        return image
    size = (max_size, max_size)
    image.thumbnail(size, Image.ANTIALIAS)
    image.save("Compressed_"+image, optimize=True, quality=85)
    return image

@st.cache(suppress_st_warning=True, allow_output_mutation=True, show_spinner=False)
def read_csv(file):
    df = pd.read_csv(file)
    df1 = df.copy()
    return df

@st.cache(suppress_st_warning=True, allow_output_mutation=True, show_spinner=False)
def read_excel(file):
    df = pd.read_excel(file, engine='openpyxl')
    df1 = df.copy()
    return df

@st.cache(suppress_st_warning=True, allow_output_mutation=True, show_spinner=False)
def select_excel_sheet(file):
    sheets = pd.read_excel(file, sheet_name=None, engine='openpyxl')
    sheet_names = list(sheets.keys())
    sheet_names.sort()
    return sheets, sheet_names

@st.cache(suppress_st_warning=True, allow_output_mutation=True, show_spinner=False)
def read_xlsx_as_bytes(file):
    with open(file, 'rb') as f:
        data = f.read()
    return data

st.set_page_config(layout="centered", page_icon='🐍')
st.set_option('deprecation.showPyplotGlobalUse', False)
st.title('Redução de imagens e tratamento de arquivos em excel')
st.header('''
    A ferramenta permite ao usuário:
        1. Reduzir o tamanho de imagens sem perder a qualidade;
        2. Reduzir o tamanho de arquivos CSV e Excel ajustando os tipos de dados;
    Idealmente, para os arquivos em excel, recomendo que estejam em formato base de dados. Para continuar, é necessário que o usuário selecione o arquivo que deseja, e a ferramenta identificará a extensão automaticamente.
''')

footer="""<style>
a:link , a:visited{
color: blue;
background-color: transparent;
text-decoration: underline;
}

a:hover,  a:active {
color: red;
background-color: transparent;
text-decoration: underline;
}

.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
background-color: transparent;
color: white;
text-align: center;
}
</style>
<div class="footer">
<p>Developed with ❤ by <a style='display: block; color: white; text-align: center;' href="https://www.linkedin.com/in/thiago-bellotto/" target="_blank">Thiago Bellotto</a></p>
</div>
"""
st.markdown(footer,unsafe_allow_html=True)



file = st.file_uploader("", type=["csv", "xlsx", "jpeg", "png", "jpg"], )
if not file:
    st.stop()

with st.spinner(text='Lendo o arquivo. Aguarde...'):
    extension = file.name.split('.')[-1]
    
    if extension in ['jpeg', 'png', 'jpg']:
        image = reduce_image_size_without_losing_quality(file)
    elif extension in ['xlsx', 'xls']:
        df, sheet_names = select_excel_sheet(file)
        sheet_name = st.selectbox("Selecione a aba:", sheet_names)
        df = df[sheet_name]
        file_name = file.name.replace('.xlsx', '').replace('.xls', '')
        st.text('Número de linhas: {}'.format(df.shape[0]))
        st.text('Número de colunas: {}'.format(df.shape[1]))
        my_expander = st.expander(label='Visualizar planilha')
        try:
            with my_expander:
                st.dataframe(df, width=800)
        except StreamlitAPIException:
            with my_expander:
                st.text('Não foi possível exibir o arquivo.')
    elif extension == 'csv':
        df = read_csv(file)
        file_name = file.name.replace('.csv', '')
        st.text('Número de linhas: {}'.format(df.shape[0]))
        st.text('Número de colunas: {}'.format(df.shape[1]))
        my_expander = st.expander(label='Visualizar planilha')
        try:
            with my_expander:
                st.dataframe(df, width=800)
        except StreamlitAPIException:
            with my_expander:
                st.text('Não foi possível exibir o arquivo.')
    else:
        st.warning("Formato de arquivos não permitido. Em caso de dúvidas, entrar em contato com Thiago Bellotto.")
        st.stop()


if st.button('Realizar conversões'):
    with st.spinner(text='Realizando conversões... Aguarde.'):
        
        try:
            st.image(image, caption='Para salvar a imagem, clique com o botão direto e vá em "Salvar imagem como".')
        except NameError:
            try:
                if df.empty:
                    st.warning('Nenhum dado encontrado.')
                elif df.shape[1] == 1:
                    st.text('Não é possível gerar análises com apenas uma coluna.')
                elif df.shape[1] == 2:
                    st.text('Não é possível gerar análises com apenas duas colunas.')
                else:
                    df = reduce_precision(df)
                    towrite = io.BytesIO()
                    downloaded_file = df.to_excel(towrite, encoding='utf-8', index=False, header=True) # write to BytesIO buffer
                    towrite.seek(0)  # reset pointer
                    b64 = base64.b64encode(towrite.read()).decode() 
                    linko = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{file_name}.xlsx">Download excel</a>'
                    st.markdown(linko, unsafe_allow_html=True)
            except:
                st.warning('Não foi possível gerar as conversões.')

