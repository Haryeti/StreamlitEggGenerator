import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from stl import mesh
import io
import stl
import tempfile
import os
from scipy import integrate

def egg_equation(x, B, L, D_L4, n):
    a = L / 2
    b = B / 2
    k = (D_L4 / L) - 0.5  # Adjusts the "pointiness" of the egg
    c = n / 10  # Affects the overall shape
    y = b * np.sqrt(1 - (x / a)**2) * (1 + c * (x / a) + k * (x / a)**2)
    return y

def calculate_egg_volume(B, L, D_L4, n):
    # Calculate volume using numerical integration
    a = L / 2
    b = B / 2
    k = (D_L4 / L) - 0.5
    c = n / 10

    def integrand(x):
        y = egg_equation(x, B, L, D_L4, n)
        return np.pi * y**2

    volume, _ = integrate.quad(integrand, -a, a)
    return volume

def generate_2d_preview(B, L, D_L4, n,auto_scale):
    x = np.linspace(-L/2, L/2, 1000)
    y = egg_equation(x, B, L, D_L4, n)
    
    # Calculate the scaling factor
    max_width = np.max(y) * 2
    scale_factor = B / max_width
    
    y_scaled = y * scale_factor
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(x, y_scaled, '#BE1E2D')
    ax.plot(x, -y_scaled, '#BE1E2D')
    
    # Fill the egg shape with a lighter shade
    ax.fill_between(x, y_scaled, -y_scaled, color='#FFA07A', alpha=0.5)
    
    ax.set_title("2D Egg Preview")
    ax.set_aspect('equal', 'box')
    ax.grid(True)

    if auto_scale:
        margin = 0.1  # 10% margin
        x_margin = L * margin
        y_margin = B * margin
        ax.set_xlim(-L/2 - x_margin, L/2 + x_margin)
        ax.set_ylim(-B/2 - y_margin, B/2 + y_margin)
    else:
        ax.set_xlim(-80, 80)
        ax.set_ylim(-70, 70)

    # Set the axis labels with units
    ax.set_xlabel("mm")
    ax.set_ylabel("mm")

    return fig

def generate_3d_model(B, L, D_L4, n):
    # Generate non-linear spacing for x
    num_l_points = int((L * 1.16) +50 )
    num_w_points = int((B *1.16) +50)

    t = np.linspace(0, np.pi, num_w_points)
    x = (L/2) * np.cos(t)
    
    theta = np.linspace(0, 2*np.pi, num_l_points)
    X, Theta = np.meshgrid(x, theta)
    
    R = egg_equation(X, B, L, D_L4, n)
    
    # Calculate the scaling factor
    max_width = np.max(R) * 2
    scale_factor = B / max_width
    
    R_scaled = R * scale_factor
    
    Y = R_scaled * np.cos(Theta)
    Z = R_scaled * np.sin(Theta)
    
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
    st.markdown("<h1 style='text-align: center;'>3D Egg Generator</h1>", unsafe_allow_html=True)

    # Define the bird species and their egg parameters
    bird_species = {
        "Common Loon": {"B": 56.0, "L": 89.0, "D_L4": 33.9, "n": 1.37},
        "Coturnix Quail": {"B": 27.0, "L": 35.0, "D_L4": 15.0, "n": 1.6},
        "Black-capped Chickadee": {"B": 12.0, "L": 15.0, "D_L4": 7.0, "n": 1.11},
        "Snow Bunting": {"B": 16.5, "L": 22.9, "D_L4": 12.0, "n": 1.25},
        "Domestic Chicken": {"B": 40.0, "L": 58.0, "D_L4": 25.0, "n": 2.0},
        "Domestic Duck": {"B": 44.0, "L": 65.0, "D_L4": 35.6, "n": 1.4},
        "Canada Goose": {"B": 56.6, "L": 83.87, "D_L4": 48.6, "n": 1.0},
        "Ostrich": {"B": 130.0, "L": 150.0, "D_L4": 75.0, "n": 0.5},
        "Rhea": {"B": 90.0, "L": 130.0, "D_L4": 51.0, "n": 0.87},
        "Elephant Bird": {"B": 245.0, "L": 340.0, "D_L4": 140.0, "n": 1.25}
    }

    if 'selected_species' not in st.session_state:
        st.session_state.selected_species = "Domestic Chicken"
        st.session_state.B = 50.0
        st.session_state.L = 70.0
        st.session_state.D_L4 = 25.0
        st.session_state.n = 2.0
        st.session_state.auto_scale = False

    # Add a sidebar with a list of bird species
    with st.sidebar:
        # Add a toggleable button that sorts by length or by name
        sort_by_length = st.checkbox("Sort by length")

        # Sort the list of bird species by egg length or by name
        if sort_by_length:
            sorted_species = sorted(bird_species.keys(), key=lambda x: bird_species[x]["L"])
        else:
            sorted_species = sorted(bird_species.keys())

        # Create buttons for species selection
        for species in sorted_species:
            if st.button(
                species,
                key=f"button_{species}",
            ):
                st.session_state.selected_species = species
                if species != "Custom":
                    st.session_state.B = bird_species[species]["B"]
                    st.session_state.L = bird_species[species]["L"]
                    st.session_state.D_L4 = bird_species[species]["D_L4"]
                    st.session_state.n = bird_species[species]["n"]

        st.markdown("---")   
        st.markdown("<p style='text-align: center;'>If you determine the parameters for a species of bird's egg, let me know and I'll add it to the program!</p>", unsafe_allow_html=True)

    with st.container(border=True):
        
        st.markdown("<h2>Parameters</h2>", unsafe_allow_html=True)
        col1, col2 = st.columns([7, 1])
        L = col1.slider("Length (mm)", 10.0, 160.0, st.session_state.L, 0.1)
        L_text = col2.text_input("Length", value=str(L), key="L_text", label_visibility="hidden")
        B = col1.slider("Width (mm)", 5.0, 150.0, st.session_state.B, 0.1)
        B_text = col2.text_input("Width", value=str(B), key="B_text", label_visibility="hidden")
        D_L4 = col1.slider("End roundness", 0.1, B, st.session_state.D_L4, 0.1)
        D_L4_text = col2.text_input("Roundness", value=str(D_L4), key="D_L4_text", label_visibility="hidden")
        n = col1.slider("Diameter location", 0.01, 7.0, st.session_state.n, 0.01)
        n_text = col2.text_input("Diameter locus", value=str(n), key="n_text", label_visibility="hidden")

        # Update the slider values with the text input values
        if B_text:
            B = float(B_text)
        if L_text:
            L = float(L_text)
        if D_L4_text:
            D_L4 = float(D_L4_text)
        if n_text:
            n = float(n_text)

    # Calculate egg volume
    volume = calculate_egg_volume(B, L, D_L4, n)/1000



    with st.container(border=True):
        # Display egg volume
        col3, col4 = st.columns([1,3])
        density = col3.number_input("Density(g/cm³)", value=1.031, key="density",step=0.001,format="%.3f")
        col4.markdown(f"<h3>Calculated Egg Volume: {volume:.2f} cm³</h3>", unsafe_allow_html=True)
        col4.markdown(f"<h3>Theoretical Egg Mass: {(float(volume)*float(density)):.2f} g</h3>", unsafe_allow_html=True)


    auto_scale = st.checkbox("Auto-scale 2D preview", value=st.session_state.auto_scale, key="auto_scale_checkbox")

    fig = generate_2d_preview(B, L, D_L4, n, auto_scale)
    st.pyplot(fig)
    
    col1, col2 = st.columns(2)  # Create two columns with equal width
    
    stl_data = None  # Define stl_data variable outside of the if block
    file_name = "SaviMadeEgg.stl"  # Define default file name
    
    if col1.button("Generate 3D Model"):
        with st.spinner("Generating 3D model..."):
            stl_file = generate_3d_model(B, L, D_L4, n)
            
            # Read the binary STL data from the temporary file
            with open(stl_file, "rb") as f:
                stl_data = f.read()
            
            # Delete the temporary file
            os.remove(stl_file)
            
            st.success("3D model generated successfully!")
    
    if stl_data is not None:
        # Prompt the user for a file name
        file_name = st.text_input("Enter a file name", value="SaviMadeEgg(Parameters-_" + str(L_text) + "_" + str(B_text) + "_" + str(D_L4_text) + "_" + str(n_text) +")") + ".stl"

        # Save the STL file with the user-specified file name
        col2.download_button(
            label="Download STL",
            data=stl_data,
            file_name=file_name,
            mime="application/octet-stream"
        )
        pass

# Add credits to the bottom of the app
    st.markdown("---")
    st.markdown("<p style='text-align: center;'>Created by Lincoln Savi of Savimade.ca | <a href='https://savimade.ca/contact'>Contact</a></p>", unsafe_allow_html=True)
    

if __name__ == "__main__":
    main()