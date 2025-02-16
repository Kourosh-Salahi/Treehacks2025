import React, { useEffect } from 'react';
import { View, Text } from 'react-native';
import { initTerra } from 'terra-react'; // Assuming this is the Terra SDK

const App = () => {
  useEffect(() => {
    const initializeTerra = async () => {
      try {
        const devID = 'YOUR_DEV_ID';
        const referenceId = 'YOUR_REFERENCE_ID';
            
        const successMessage = await initTerra(devID, referenceId);
        console.log('Terra initialized successfully:', successMessage);
      } catch (error) {
        console.error('Failed to initialize Terra:', error);
      }
    };

    initializeTerra();  // Call this when the app launches
  }, []);  // Empty dependency array means it runs only once, when the component mounts

  return (
    <View>
      <Text>Welcome to the App using Terra</Text>
    </View>
  );
};

export default App;
