import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from stl import mesh
import io
import stl
import tempfile
import os

def egg_equation(x, B, L, D_L4, n):
    a = L / 2
    b = B / 2
    k = (D_L4 / L) - 0.5  # Adjusts the "pointiness" of the egg
    c = n / 10  # Affects the overall shape
    y = b * np.sqrt(1 - (x / a)**2) * (1 + c * (x / a) + k * (x / a)**2)
    return y

def generate_2d_preview(B, L, D_L4, n):
    x = np.linspace(-L/2, L/2, 1000)
    y = egg_equation(x, B, L, D_L4, n)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(x, y, 'b-')
    ax.plot(x, -y, 'b-')
    ax.set_title("2D Egg Preview")
    ax.set_aspect('equal', 'box')
    ax.grid(True)
    ax.set_xlim(-L/2 - 0.5, L/2 + 0.5)
    ax.set_ylim(-B/2 - 0.5, B/2 + 0.5)
    return fig

def generate_3d_model(B, L, D_L4, n):
    theta = np.linspace(0, 2*np.pi, 200)
    x = np.linspace(-L/2, L/2, 100)
    X, Theta = np.meshgrid(x, theta)
    
    R = egg_equation(X, B, L, D_L4, n)
    Y = R * np.cos(Theta)
    Z = R * np.sin(Theta)
    
    vertices = np.column_stack([X.flatten(), Y.flatten(), Z.flatten()])
    
    faces = []
    n_theta, n_x = Theta.shape
    for i in range(n_theta - 1):
        for j in range(n_x - 1):
            v0 = i * n_x + j
            v1 = v0 + 1
            v2 = (i + 1) * n_x + j
            v3 = v2 + 1
            faces.extend([[v0, v1, v2], [v1, v3, v2]])
    
    egg_mesh = mesh.Mesh(np.zeros(len(faces), dtype=mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        for j in range(3):
            egg_mesh.vectors[i][j] = vertices[f[j],:]
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as temp:
        egg_mesh.save(temp.name, mode=stl.Mode.BINARY)
        return temp.name

def main():
    st.markdown("<h1 style='text-align: center; color: #BE1E2D; font-family: Permanent Marker;'>3D Egg Generator</h1>", unsafe_allow_html=True)

    with st.container():
        st.markdown("<h2 style='color: #b78989; font-family: Permanent Marker;'>Parameters</h2>", unsafe_allow_html=True)
        B = st.slider("Maximum width", 1.0, 10.0, 5.0, 0.1)
        L = st.slider("Maximum length", 1.0, 15.0, 7.0, 0.1)
        D_L4 = st.slider("Diameter at L/4", 0.1, B, B/2, 0.1)
        n = st.slider("Shape parameter", 0.1, 10.0, 2.0, 0.1)

        fig = generate_2d_preview(B, L, D_L4, n)
        st.pyplot(fig)

    col1, col2 = st.columns(2)  # Create two columns with equal width

    stl_data = None  # Define stl_data variable outside of the if block

    if col1.button("Generate 3D Model"):
        with st.spinner("Generating 3D model..."):
            stl_file = generate_3d_model(B, L, D_L4, n)

            # Read the binary STL data from the temporary file
            with open(stl_file, "rb") as f:
                stl_data = f.read()

            # Delete the temporary file
            os.remove(stl_file)

            st.success("3D model generated successfully!")

    if stl_data is not None and col2.download_button(
        label="Download STL",
        data=stl_data,
        file_name="egg_model.stl",
        mime="application/octet-stream"
    ):
        pass

def generate_2d_preview(B, L, D_L4, n):
    x = np.linspace(-L/2, L/2, 1000)
    y = egg_equation(x, B, L, D_L4, n)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(x, y, '#BE1E2D')
    ax.plot(x, -y, '#BE1E2D')
    ax.set_title("2D Egg Preview")
    ax.set_aspect('equal', 'box')
    ax.grid(True)
    ax.set_xlim(-7.5, 7.5)  # Set the limits of the x-axis
    ax.set_ylim(-5.5, 5.5)  # Set the limits of the y-axis
    return fig

if __name__ == "__main__":
    main()
