import streamlit as st
import pandas as np

st.set_page_config(
    page_title="🐎 KimiK2 Horse Racing Predictor",
    page_icon="🐎",
    layout="wide"
)

class HorseRacingPredictor:
    def __init__(self):
        self.weights = {
            'speed_figure': 0.25,
            'recent_form': 0.20,
            'class_level': 0.15,
            'jockey_skill': 0.12,
            'trainer_stats': 0.12,
            'post_position': 0.08,
            'track_condition': 0.05,
            'distance_fitness': 0.03
        }

    def calculate_overall_score(self, horse_data):
        # Simple scoring for demo
        speed = horse_data.get('beyer_speed_figure', 70)
        form = sum(horse_data.get('recent_finishes', [5,5,5])) / len(horse_data.get('recent_finishes', [5,5,5]))
        return speed - (form * 2)

    def predict_race(self, horses_data):
        results = []
        
        for horse in horses_data:
            score = self.calculate_overall_score(horse)
            results.append({
                'Horse': horse.get('name', 'Unknown'),
                'Score': round(score, 2),
                'Win_Probability': round(max(0, score - 60), 1)
            })
        
        results_df = pd.DataFrame(results).sort_values('Score', ascending=False)
        return results_df

def main():
    st.title("🏇 KimiK2 Horse Racing Predictor")
    st.subheader("AI-Powered Race Analysis & Predictions")

    if 'horses' not in st.session_state:
        st.session_state.horses = []

    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("🐎 Add Horse")
        
        horse_name = st.text_input("Horse Name")
        
        col_h1, col_h2 = st.columns(2)
        
        with col_h1:
            beyer_figure = st.number_input("Beyer Speed Figure", 50, 120, 85)
            recent_finishes = st.text_input("Recent Finishes", "2,1,3")
        
        with col_h2:
            post_position = st.number_input("Post Position", 1, 15, 1)

        if st.button("🐎 Add Horse"):
            try:
                recent_finishes_list = [int(x.strip()) for x in recent_finishes.split(',')]
                
                horse_data = {
                    'name': horse_name,
                    'beyer_speed_figure': beyer_figure,
                    'recent_finishes': recent_finishes_list,
                    'post_position': post_position
                }
                
                st.session_state.horses.append(horse_data)
                st.success(f"✅ Added {horse_name}!")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    with col2:
        st.header("📊 Race Info")
        
        if st.session_state.horses:
            st.metric("Horses Entered", len(st.session_state.horses))
            
            for i, horse in enumerate(st.session_state.horses, 1):
                st.write(f"{i}. {horse['name']}")
        else:
            st.info("Add horses above")

    # Predictions
    if len(st.session_state.horses) >= 2:
        st.header("🔮 AI Predictions")
        
        predictor = HorseRacingPredictor()
        predictions = predictor.predict_race(st.session_state.horses)
        
        st.subheader("🏆 Top 5 Predictions")
        
        col_pred1, col_pred2 = st.columns(2)
        
        with col_pred1:
            st.dataframe(predictions.head(5))
        
        with col_pred2:
            st.bar_chart(predictions.head(5).set_index('Horse')['Win_Probability'])

        # Export
        csv = predictions.to_csv(index=False)
        st.download_button("📊 Download CSV", csv, "predictions.csv", "text/csv")
        
        if st.button("🗑️ Clear All"):
            st.session_state.horses = []
            st.rerun()

if __name__ == "__main__":
    main()
