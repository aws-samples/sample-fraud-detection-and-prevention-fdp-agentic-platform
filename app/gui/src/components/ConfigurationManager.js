// Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { useState, useEffect } from 'react';
import { apiGet, apiPut } from '../utils/api';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Checkbox,
  Slider,
} from '@mui/material';

function ConfigurationManager({ accessToken }) {
  const [modelConfigs, setModelConfigs] = useState([]);
  const [inferenceConfigs, setInferenceConfigs] = useState([]);

  useEffect(() => {
    if (accessToken) {
      fetchConfigurations();
    }
  }, [accessToken]);

  const fetchConfigurations = async () => {
    console.log('Fetching configurations...', accessToken);

    try {
      const modelResponse = await apiGet('/configurations?config_id=MODEL_IDS', accessToken);
      const inferenceResponse = await apiGet('/configurations?config_id=INFERENCE_PARAMS', accessToken);
      setModelConfigs(modelResponse);
      setInferenceConfigs(inferenceResponse);
    } catch (error) {
      console.error('Error details:', {
        message: error.message,
        response: error.response,
        stack: error.stack
      });
      handleAPIError(error);
    }
  };

  const handleUpdate = async (config) => {
    try {
      if (config.pk === 'MODEL_IDS' && config.is_active) {
        setModelConfigs(prevConfigs => 
          prevConfigs.map(modelConfig => ({
            ...modelConfig,
            is_active: modelConfig.sk === config.sk
          }))
        );

        // Deactivate all other models in the backend
        const updates = modelConfigs.map(modelConfig => {
          if (modelConfig.sk !== config.sk) {
            return apiPut('/configurations', accessToken, {
              body: { ...modelConfig, is_active: false }
            });
          }
          return Promise.resolve();
        });

        await Promise.all(updates);
      }

      // Update the current config
      const data = await apiPut('/configurations', accessToken, {
        body: config
      });
      await fetchConfigurations();
    } catch (error) {
      handleAPIError(error);
      await fetchConfigurations();
    }
  };


  const handleAPIError = (error) => {
    console.error('API Error:', error);
    let errorMessage = 'An unexpected error occurred';
  
    if (error.response) {
      errorMessage = (
        error.response.data.message ||
        error.response.data.error ||
        `Error: ${error.response.status}`
      );
    } else if (error.message) {
      errorMessage = error.message;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" sx={{ mb: 3 }}>
        Configuration Manager
      </Typography>

      <Typography variant="h6" sx={{ mb: 2 }}>
        Model IDs
      </Typography>
      <TableContainer component={Paper} sx={{ mb: 4 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Key</TableCell>
              <TableCell>Value</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Active</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {modelConfigs.map((config) => (
              <ConfigurationRow 
                key={config.sk} 
                config={config} 
                onUpdate={handleUpdate}
                isModelConfig={true}
              />
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Typography variant="h6" sx={{ mb: 2 }}>
        Inference Parameters
      </Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Key</TableCell>
              <TableCell>Value</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {inferenceConfigs.map((config) => (
              <ConfigurationRow 
                key={config.sk} 
                config={config} 
                onUpdate={handleUpdate}
                isModelConfig={false}
              />
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

function ConfigurationRow({ config, onUpdate, isModelConfig }) {
    const [isEditing, setIsEditing] = useState(false);
    const [value, setValue] = useState(config.value);
    const [isActive, setIsActive] = useState(config.is_active || false);

    useEffect(() => {
        setIsActive(config.is_active || false);
    }, [config.is_active]);

    const getSliderConfig = (sk) => {
        switch (sk) {
            case 'temperature':
            case 'top_p':
                return {
                    min: 0,
                    max: 1,
                    step: 0.01,
                    marks: [
                        { value: 0, label: '0' },
                        { value: 0.5, label: '0.5' },
                        { value: 1, label: '1' }
                    ]
                };
            case 'top_k':
                return {
                    min: 0,
                    max: 500,
                    step: 1,
                    marks: [
                        { value: 0, label: '0' },
                        { value: 250, label: '250' },
                        { value: 500, label: '500' }
                    ]
                };
            case 'max_new_tokens':
                return {
                    min: 1,
                    max: 64000,
                    step: 1,
                    marks: [
                        { value: 1, label: '1' },
                        { value: 32000, label: '32K' },
                        { value: 64000, label: '64K' }
                    ]
                };
            default:
                return null;
        }
    };

    const handleSave = () => {
        onUpdate({ ...config, value, is_active: isActive });
        setIsEditing(false);
    };

    const handleActiveChange = (event) => {
        const newIsActive = event.target.checked;
        if (newIsActive) {
            setIsActive(newIsActive);
            onUpdate({ ...config, value, is_active: newIsActive });
        }
    };

    const handleSliderChange = (event, newValue) => {
        setValue(String(newValue));
    };

    const handleTextChange = (e) => {
        const newValue = e.target.value;
        const sliderConfig = getSliderConfig(config.sk);
        
        if (sliderConfig) {
            const numValue = Number(newValue);
            if (!isNaN(numValue) && numValue >= sliderConfig.min && numValue <= sliderConfig.max) {
                setValue(newValue);
            }
        } else {
            setValue(newValue);
        }
    };

    const isInferenceParam = ['temperature', 'top_p', 'top_k', 'max_new_tokens'].includes(config.sk);
    const sliderConfig = getSliderConfig(config.sk);

    return (
        <TableRow>
            <TableCell>{config.sk}</TableCell>
            <TableCell>
                {isEditing ? (
                    <Box sx={{ width: '100%' }}>
                        {isInferenceParam && sliderConfig ? (
                            <>
                                <Box sx={{ width: 300, mb: 2 }}>
                                    <Slider
                                        value={Number(value)}
                                        onChange={handleSliderChange}
                                        {...sliderConfig}
                                        valueLabelDisplay="auto"
                                    />
                                </Box>
                                <TextField
                                    value={value}
                                    onChange={handleTextChange}
                                    size="small"
                                    type="number"
                                    inputProps={{
                                        min: sliderConfig.min,
                                        max: sliderConfig.max,
                                        step: sliderConfig.step
                                    }}
                                />
                            </>
                        ) : (
                            <TextField
                                value={value}
                                onChange={handleTextChange}
                                size="small"
                            />
                        )}
                    </Box>
                ) : (
                    value
                )}
            </TableCell>
            <TableCell>{config.description}</TableCell>
            {isModelConfig && (
                <TableCell>
                    <Checkbox
                        checked={isActive}
                        onChange={handleActiveChange}
                        disabled={!isEditing}
                    />
                </TableCell>
            )}
            <TableCell>
                {isEditing ? (
                    <Button onClick={handleSave}>Save</Button>
                ) : (
                    <Button onClick={() => setIsEditing(true)}>Edit</Button>
                )}
            </TableCell>
        </TableRow>
    );
}

export default ConfigurationManager;
