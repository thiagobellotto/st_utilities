#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import streamlit as st
from streamlit.legacy_caching.caching import cache
import os
import time
import numpy as np
from PIL import Image

@cache
def reduce_precision(df):
        cols_to_convert = []
        date_strings = ['_date', 'date_', 'date', 'data', 'Data', 'Datas', 'datas']

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

@cache
def reduce_image_size_without_losing_quality(image_path, max_size=8164):
    """
    Reduce the size of an image without losing the image quality.
    """
    image = Image.open(image_path)
    width, height = image.size
    print(width, height)
    if width <= max_size and height <= max_size:
        return image
    size = (max_size, max_size)
    image.thumbnail(size, Image.ANTIALIAS)
    image.save("Compressed_"+image, optimize=True, quality=85)
    return image

@cache
def read_csv(file):
    df = pd.read_csv(file)
    df1 = df.copy()
    return df

@cache
def read_excel(file):
    df = pd.read_excel(file)
    df1 = df.copy()
    return df

st.set_page_config(layout="centered", page_icon="random") 
st.set_option('deprecation.showPyplotGlobalUse', False)
st.title('Ferramentas - Bellotto')
st.header('Por favor, selecione o arquivo e selecione a funcionalidade desejada.')

file = st.file_uploader("Insira o arquivo abaixo:", )
if not file:
    st.stop()

with st.spinner(text='Lendo o arquivo. Aguarde...'):
    extension = file.name.split('.')[-1]
    
    if extension in ['jpeg', 'png', 'jpg']:
        image = reduce_image_size_without_losing_quality(file)
    elif extension in ['xlsx', 'xls']:
        df = read_excel(file)
    elif extension == 'csv':
        df = read_csv(file)
    else:
        st.warning("Formato de arquivos não permitido. Em caso de dúvidas, entrar em contato com Thiago Bellotto.")
        st.stop()

if st.button('Gerar análises'):
    with st.spinner(text='Realizando conversões... Aguarde.'):
        
        try:
            st.image(image)
        except NameError:
            if df.empty:
                st.warning('Nenhum dado encontrado.')
            elif df.shape[1] == 1:
                st.text('Não é possível gerar análises com apenas uma coluna.')
            elif df.shape[1] == 2:
                st.text('Não é possível gerar análises com apenas duas colunas.')
            else:
                df = reduce_precision(df)
                st.text('Número de linhas: {}'.format(df.shape[0]))
                st.text('Número de colunas: {}'.format(df.shape[1]))
                st.dataframe(df, width=800)

                st.download_button(label = 'Download CSV', data = df.to_csv(index=False), file_name = 'arquivo_reduzido.csv', mime = 'text/csv')