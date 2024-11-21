app_css = """
<style>
/* Background and header styling */
.block-container {
    padding: 2rem;
    background-color: #f9f9f9;
}
[data-testid="stHeader"] { padding-top: 0.5rem; padding-bottom: 0.5rem; height: 0rem; background-color: #f0f2f6; }
.main-title {
    color: #1F618D;
    font-weight: bold;
    text-align: center;
    font-size: 2.3rem;
}
.image-container img {
        width: 20px;  /* Set your desired width */
        height: 300px;  /* Set your desired height */
    }
    

.instructions-title {
    color: #1F618D;
    font-weight: bold;
    text-align: left;
    font-size: 2.rem;
}
.subheader {
    color: #2E4053;
    font-weight: bold;
    font-size: 1.5rem;
    margin-top: 1rem;
    margin-bottom: 0.5rem;
}
/* Sidebar styling */
.sidebar .sidebar-content {
    background-color: #AED6F1;
    padding: 1rem;
    border-radius: 10px;
}
.sidebar .sidebar-content h1 {
    color: #1F618D;
}
.stButton > button {
    color: #FFFFFF;
    background-color: #1F618D;
    border: None;
}
/* Alert and success message styling */
.stAlert, .stSuccess, .stError {
    padding: 0.75rem 1.5rem;
    border-radius: 10px;
    font-weight: bold;
}
/* DataFrame and map styling */
.stDataFrame, .stMap {
    border-radius: 10px;
}
</style>
"""
