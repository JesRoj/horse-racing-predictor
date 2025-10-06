import streamlit as st

# Simple horse racing predictor
st.title("🏇 KimiK2 Horse Racing Predictor")
st.subheader("AI-Powered Race Analysis & Predictions")

if 'horses' not in st.session_state:
    st.session_state.horses = []

# Add horse section
st.header("🐎 Add Horse")
col1, col2 = st.columns(2)

with col1:
    horse_name = st.text_input("Horse Name")
    speed_figure = st.number_input("Speed Figure (50-120)", 50, 120, 85)

with col2:
    recent_form = st.slider("Recent Form Rating (1-10)", 1, 10, 7)
    post_position = st.number_input("Post Position", 1, 15, 1)

if st.button("🐎 Add Horse"):
    if horse_name:
        horse_data = {
            'name': horse_name,
            'speed': speed_figure,
            'form': recent_form,
            'post': post_position
        }
        st.session_state.horses.append(horse_data)
        st.success(f"✅ Added {horse_name}!")
        st.rerun()
    else:
        st.error("Please enter a horse name")

# Show current horses
if st.session_state.horses:
    st.header("📊 Current Entries")
    for i, horse in enumerate(st.session_state.horses, 1):
        st.write(f"{i}. {horse['name']} (Speed: {horse['speed']}, Form: {horse['form']})")

# Predictions
if len(st.session_state.horses) >= 2:
    st.header("🔮 AI Predictions")
    
    # Simple scoring algorithm
    predictions = []
    for horse in st.session_state.horses:
        # Simple score: speed + form - post_position_penalty
        post_penalty = max(0, (horse['post'] - 8) * 2)  # Outside posts penalized
        score = horse['speed'] + (horse['form'] * 2) - post_penalty
        
        predictions.append({
            'Horse': horse['name'],
            'Score': score,
            'Win Probability': max(0, score - 100)
        })
    
    # Sort by score
    predictions.sort(key=lambda x: x['Score'], reverse=True)
    
    st.subheader("🏆 Top Predictions")
    
    # Display top 5
    for i, horse in enumerate(predictions[:5], 1):
        st.write(f"{i}. **{horse['Horse']}** - Score: {horse['Score']:.1f}")
    
    # Simple bar chart
    if st.button("🔄 Refresh Predictions"):
        st.rerun()
    
    if st.button("🗑️ Clear All Horses"):
        st.session_state.horses = []
        st.rerun()

else:
    st.info("🐎 Add at least 2 horses to see predictions!")
