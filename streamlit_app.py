import streamlit as st
import subprocess
import sys

st.title("Tennis Team Scheduler")

st.markdown("### Workflow Steps")
st.info("This will execute: Input → Scheduler → Run File")

if st.button("Start Scheduling Process"):
    st.subheader("Step 1: Processing Input")
    try:
        # Run the input file
        result = subprocess.run([sys.executable, "input"], capture_output=True, text=True)
        st.success("✓ Input file processed")
        if result.stdout:
            st.write(result.stdout)
        if result.stderr:
            st.warning(result.stderr)
    except Exception as e:
        st.error(f"Error in input step: {e}")
        st.stop()
    
    st.subheader("Step 2: Running Scheduler")
    try:
        # Run the scheduler
        result = subprocess.run([sys.executable, "scheduler"], capture_output=True, text=True)
        st.success("✓ Scheduler executed")
        if result.stdout:
            st.write(result.stdout)
        if result.stderr:
            st.warning(result.stderr)
    except Exception as e:
        st.error(f"Error in scheduler step: {e}")
        st.stop()
    
    st.subheader("Step 3: Running Final Output")
    try:
        # Run the run file
        result = subprocess.run([sys.executable, "run file"], capture_output=True, text=True)
        st.success("✓ Run file executed")
        if result.stdout:
            st.write(result.stdout)
        if result.stderr:
            st.warning(result.stderr)
    except Exception as e:
        st.error(f"Error in run file step: {e}")
        st.stop()
    
    st.success("✓ All steps completed successfully!")
