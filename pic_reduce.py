#!/usr/bin/env python
# coding: utf-8

import streamlit as st
from streamlit.errors import StreamlitAPIException
from PIL import Image

st.set_page_config(layout="centered", page_icon='🐍')
st.set_option('deprecation.showPyplotGlobalUse', False)
st.title('Ferramenta para redução do tamanho de imagens')
st.header('''
    A ferramenta permite ao usuário reduzir o tamanho de imagens sem perder a qualidade.
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
st.markdown(footer, unsafe_allow_html=True)

file = st.file_uploader("", type=["jpeg", "png", "jpg"], )

if not file:
    st.stop()

## increase space
st.markdown("")

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
    return image

if st.button('Converter imagem', key='converter'):
    with st.spinner(text='Convertendo a imagem... Aguarde.'):
        try:
            image = reduce_image_size_without_losing_quality(file).convert('RGB')
            st.image(image, caption='Para salvar a imagem, clique com o botão direto e vá em "Salvar imagem como".')        
        except:
            st.warning("Não foi possível realizar a conversão. Em caso de dúvidas, entrar em contato com Thiago Bellotto.")
            st.stop()
