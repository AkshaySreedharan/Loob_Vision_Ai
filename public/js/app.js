/* ============================================================
   LOOB VISION AI - REACT + REACT BOOTSTRAP INDUSTRIAL UI
   ============================================================ */

const { useState, useEffect, useRef } = React;
const {
  Container, Row, Col, Card, Button, Navbar, Badge,
  Form, Spinner, Accordion, Alert, Table, Stack
} = ReactBootstrap;

// ============================================================
// HEADER COMPONENT
// ============================================================
function Header({ modelStatus, selectedModel, onModelChange }) {
  return (
    <Navbar className="loob-navbar sticky-top">
      <Container fluid className="px-3 px-md-4">
        <Navbar.Brand href="#" className="d-flex align-items-center gap-3">
          <div className="d-flex align-items-center justify-content-center"
               style={{
                 width: '40px',
                 height: '40px',
                 borderRadius: '10px',
                 background: 'linear-gradient(135deg, #00b8d9 0%, #0066cc 100%)',
                 boxShadow: '0 0 15px rgba(0,184,217,0.4)',
                 color: '#fff'
               }}>
            <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/>
            </svg>
          </div>
          <div>
            <div className="loob-brand-title">LUBVISION</div>
            <div className="loob-brand-subtitle">AI-Powered Lubricant Condition Analysis</div>
          </div>
        </Navbar.Brand>

        <div className="d-flex align-items-center gap-3 ms-auto mt-2 mt-sm-0">
          <Form.Select 
            className="loob-model-select"
            value={selectedModel}
            onChange={(e) => onModelChange(e.target.value)}
            style={{ width: 'auto' }}
          >
            <option value="Original Image Model">Select Model: Original Image Model</option>
          </Form.Select>

          <span className="loob-status-badge">
            <span className="pulse-dot" style={{ background: '#00c98d', boxShadow: '0 0 8px #00c98d' }}></span>
            Model Ready
          </span>
        </div>
      </Container>
    </Navbar>
  );
}

// ============================================================
// INTERACTIVE IMAGE CROPPER COMPONENT
// ============================================================
function ImageCropper({ imageSrc, onApply, onCancel, onReset }) {
  const containerRef = useRef(null);
  const imgRef = useRef(null);
  const [crop, setCrop] = useState({ x: 10, y: 10, width: 80, height: 80 }); // Percentage (0-100)
  const [dragState, setDragState] = useState(null);

  const handleReset = () => {
    setCrop({ x: 10, y: 10, width: 80, height: 80 });
    if (onReset) onReset();
  };

  const startDrag = (mode, e) => {
    e.preventDefault();
    e.stopPropagation();
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const clientY = e.touches ? e.touches[0].clientY : e.clientY;
    setDragState({
      mode,
      startX: clientX,
      startY: clientY,
      initialCrop: { ...crop }
    });
  };

  useEffect(() => {
    const handleMove = (e) => {
      if (!dragState || !containerRef.current) return;
      const clientX = e.touches ? e.touches[0].clientX : e.clientX;
      const clientY = e.touches ? e.touches[0].clientY : e.clientY;

      const rect = containerRef.current.getBoundingClientRect();
      const deltaXPercent = ((clientX - dragState.startX) / rect.width) * 100;
      const deltaYPercent = ((clientY - dragState.startY) / rect.height) * 100;

      const init = dragState.initialCrop;
      let newCrop = { ...crop };

      if (dragState.mode === 'move') {
        newCrop.x = Math.max(0, Math.min(100 - init.width, init.x + deltaXPercent));
        newCrop.y = Math.max(0, Math.min(100 - init.height, init.y + deltaYPercent));
      } else if (dragState.mode === 'tl') {
        const newX = Math.max(0, Math.min(init.x + init.width - 15, init.x + deltaXPercent));
        const newY = Math.max(0, Math.min(init.y + init.height - 15, init.y + deltaYPercent));
        newCrop.width = init.width + (init.x - newX);
        newCrop.height = init.height + (init.y - newY);
        newCrop.x = newX;
        newCrop.y = newY;
      } else if (dragState.mode === 'tr') {
        const newY = Math.max(0, Math.min(init.y + init.height - 15, init.y + deltaYPercent));
        const newW = Math.max(15, Math.min(100 - init.x, init.width + deltaXPercent));
        newCrop.height = init.height + (init.y - newY);
        newCrop.y = newY;
        newCrop.width = newW;
      } else if (dragState.mode === 'bl') {
        const newX = Math.max(0, Math.min(init.x + init.width - 15, init.x + deltaXPercent));
        const newH = Math.max(15, Math.min(100 - init.y, init.height + deltaYPercent));
        newCrop.width = init.width + (init.x - newX);
        newCrop.x = newX;
        newCrop.height = newH;
      } else if (dragState.mode === 'br') {
        const newW = Math.max(15, Math.min(100 - init.x, init.width + deltaXPercent));
        const newH = Math.max(15, Math.min(100 - init.y, init.height + deltaYPercent));
        newCrop.width = newW;
        newCrop.height = newH;
      }

      setCrop(newCrop);
    };

    const handleEnd = () => {
      setDragState(null);
    };

    if (dragState) {
      window.addEventListener('mousemove', handleMove);
      window.addEventListener('mouseup', handleEnd);
      window.addEventListener('touchmove', handleMove, { passive: false });
      window.addEventListener('touchend', handleEnd);
    }

    return () => {
      window.removeEventListener('mousemove', handleMove);
      window.removeEventListener('mouseup', handleEnd);
      window.removeEventListener('touchmove', handleMove);
      window.removeEventListener('touchend', handleEnd);
    };
  }, [dragState, crop]);

  const applyCrop = () => {
    if (!imgRef.current) return;
    const img = imgRef.current;

    const cropX = (crop.x / 100) * img.naturalWidth;
    const cropY = (crop.y / 100) * img.naturalHeight;
    const cropW = (crop.width / 100) * img.naturalWidth;
    const cropH = (crop.height / 100) * img.naturalHeight;

    if (cropW < 10 || cropH < 10) {
      console.warn("Crop selection too small");
      return;
    }

    const maxDim = 800;
    let outW = cropW;
    let outH = cropH;

    if (Math.max(cropW, cropH) > maxDim) {
      if (cropW >= cropH) {
        outW = maxDim;
        outH = Math.round((cropH * maxDim) / cropW);
      } else {
        outH = maxDim;
        outW = Math.round((cropW * maxDim) / cropH);
      }
    }

    const canvas = document.createElement('canvas');
    canvas.width = outW;
    canvas.height = outH;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(img, cropX, cropY, cropW, cropH, 0, 0, outW, outH);

    const croppedDataUrl = canvas.toDataURL('image/jpeg', 0.85);

    const origKb = Math.round((imageSrc.length * 0.75) / 1024);
    const croppedKb = Math.round((croppedDataUrl.length * 0.75) / 1024);

    console.log("[LOOB CROP] Original dimensions:", `${img.naturalWidth} x ${img.naturalHeight} (${origKb} KB)`);
    console.log("[LOOB CROP] Cropped selection  :", `${Math.round(cropW)} x ${Math.round(cropH)}`);
    console.log("[LOOB CROP] Final upload image :", `${outW} x ${outH} (${croppedKb} KB)`);

    onApply(croppedDataUrl);
  };

  return (
    <div className="d-flex flex-column h-100 justify-content-between">
      <div className="cropper-wrapper mb-3" ref={containerRef}>
        <div className="cropper-img-container">
          <img ref={imgRef} src={imageSrc} className="cropper-img" alt="Crop target" />
          <div className="cropper-backdrop"></div>

          <div 
            className="crop-box" 
            style={{
              left: `${crop.x}%`,
              top: `${crop.y}%`,
              width: `${crop.width}%`,
              height: `${crop.height}%`
            }}
            onMouseDown={(e) => startDrag('move', e)}
            onTouchStart={(e) => startDrag('move', e)}
          >
            <div className="crop-badge">SELECT LUBRICANT REGION</div>
            <div className="crop-handle crop-handle-tl" onMouseDown={(e) => startDrag('tl', e)} onTouchStart={(e) => startDrag('tl', e)}></div>
            <div className="crop-handle crop-handle-tr" onMouseDown={(e) => startDrag('tr', e)} onTouchStart={(e) => startDrag('tr', e)}></div>
            <div className="crop-handle crop-handle-bl" onMouseDown={(e) => startDrag('bl', e)} onTouchStart={(e) => startDrag('bl', e)}></div>
            <div className="crop-handle crop-handle-br" onMouseDown={(e) => startDrag('br', e)} onTouchStart={(e) => startDrag('br', e)}></div>
          </div>
        </div>
      </div>

      <Stack direction="horizontal" gap={2} className="justify-content-center">
        <Button className="btn-loob-secondary flex-fill" onClick={handleReset}>
          <span className="me-1">↺</span> Reset
        </Button>
        <Button className="btn-loob-secondary flex-fill" onClick={onCancel}>
          <span className="me-1">✕</span> Cancel
        </Button>
        <Button className="btn-loob-primary flex-fill" onClick={applyCrop}>
          <span className="me-1">✓</span> Apply Crop
        </Button>
      </Stack>
    </div>
  );
}

// ============================================================
// CAMERA / IMAGE PREVIEW & CROP PANEL
// ============================================================
function CameraPanel({
  capturedImage,
  onCapture,
  onUpload,
  onRetake,
  onAnalyze,
  isAnalyzing
}) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const fileInputRef = useRef(null);
  const [cameraActive, setCameraActive] = useState(false);
  const [cameraError, setCameraError] = useState(null);
  const [isCropping, setIsCropping] = useState(false);
  const [uncroppedImage, setUncroppedImage] = useState(null);

  useEffect(() => {
    if (!capturedImage) {
      startCamera();
      setIsCropping(false);
      setUncroppedImage(null);
    } else {
      stopCamera();
    }

    return () => {
      stopCamera();
    };
  }, [capturedImage]);

  const startCamera = async () => {
    setCameraError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 1280 }, height: { ideal: 960 }, facingMode: 'environment' }
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
        setCameraActive(true);
      }
    } catch (err) {
      console.warn("Camera access warning:", err);
      setCameraActive(false);
      setCameraError("Camera unavailable or permission denied. Use 'Upload Image' to submit a lubricant sample.");
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject;
      stream.getTracks().forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
    setCameraActive(false);
  };

  const handleCaptureClick = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const rawWidth = video.videoWidth || 640;
      const rawHeight = video.videoHeight || 480;

      const maxDim = 800;
      let targetWidth = rawWidth;
      let targetHeight = rawHeight;

      if (Math.max(rawWidth, rawHeight) > maxDim) {
        if (rawWidth >= rawHeight) {
          targetWidth = maxDim;
          targetHeight = Math.round((rawHeight * maxDim) / rawWidth);
        } else {
          targetHeight = maxDim;
          targetWidth = Math.round((rawWidth * maxDim) / rawHeight);
        }
      }

      const canvas = canvasRef.current;
      canvas.width = targetWidth;
      canvas.height = targetHeight;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(video, 0, 0, targetWidth, targetHeight);
      const dataUrl = canvas.toDataURL('image/jpeg', 0.85);
      setUncroppedImage(dataUrl);
      onCapture(dataUrl);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (evt) => {
        const img = new Image();
        img.onload = () => {
          const maxDim = 800;
          let targetWidth = img.width;
          let targetHeight = img.height;

          if (Math.max(img.width, img.height) > maxDim) {
            if (img.width >= img.height) {
              targetWidth = maxDim;
              targetHeight = Math.round((img.height * maxDim) / img.width);
            } else {
              targetHeight = maxDim;
              targetWidth = Math.round((img.width * maxDim) / img.height);
            }
          }

          const canvas = document.createElement('canvas');
          canvas.width = targetWidth;
          canvas.height = targetHeight;
          const ctx = canvas.getContext('2d');
          ctx.drawImage(img, 0, 0, targetWidth, targetHeight);
          const dataUrl = canvas.toDataURL('image/jpeg', 0.85);
          setUncroppedImage(dataUrl);
          onUpload(dataUrl);
        };
        img.src = evt.target.result;
      };
      reader.readAsDataURL(file);
    }
  };

  const handleApplyCrop = (croppedDataUrl) => {
    setIsCropping(false);
    onCapture(croppedDataUrl);
  };

  const handleResetCrop = () => {
    if (uncroppedImage) {
      onCapture(uncroppedImage);
    }
  };

  return (
    <Card className="loob-card h-100">
      <div className="loob-card-header">
        <div className="d-flex align-items-center gap-2">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
            <circle cx="12" cy="13" r="4"/>
          </svg>
          {isCropping ? "CROP LUBRICANT REGION" : capturedImage ? "UPLOADED IMAGE PREVIEW" : "LIVE CAMERA PREVIEW"}
        </div>
        <span className="badge bg-dark text-muted border border-secondary font-monospace" style={{ fontSize: '0.72rem' }}>
          {isCropping ? "CROPPING" : capturedImage ? "IMAGE CAPTURED" : cameraActive ? "LIVE FEED" : "STANDBY"}
        </span>
      </div>

      <Card.Body className="p-3 d-flex flex-column justify-content-between">
        {!capturedImage ? (
          <div className="camera-container mb-3">
            <video ref={videoRef} className="camera-video" playsInline muted></video>
            <canvas ref={canvasRef} className="d-none"></canvas>

            {/* Square ROI Overlay Guide */}
            <div className="roi-overlay">
              <div className="roi-corner roi-top-left"></div>
              <div className="roi-corner roi-top-right"></div>
              <div className="roi-corner roi-bottom-left"></div>
              <div className="roi-corner roi-bottom-right"></div>
              <div className="roi-label">SQUARE ROI</div>
            </div>

            {!cameraActive && (
              <div className="text-center p-4 text-muted" style={{ zIndex: 5 }}>
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth="1.5" className="mb-2">
                  <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
                  <circle cx="12" cy="13" r="4"/>
                </svg>
                <div className="fw-semibold text-light mb-1">Camera Feed Offline</div>
                <div className="small text-muted mb-3">{cameraError || "Ready to capture or upload sample image."}</div>
                <Button 
                  size="sm" 
                  variant="outline-info" 
                  onClick={startCamera}
                  className="px-3"
                >
                  Enable Camera
                </Button>
              </div>
            )}
          </div>
        ) : isCropping ? (
          <ImageCropper 
            imageSrc={uncroppedImage || capturedImage}
            onApply={handleApplyCrop}
            onCancel={() => setIsCropping(false)}
            onReset={handleResetCrop}
          />
        ) : (
          <div className="preview-container mb-3">
            <img src={capturedImage} alt="Lubricant Sample" className="preview-img" />
          </div>
        )}

        {/* Hidden File Input */}
        <input 
          type="file" 
          ref={fileInputRef} 
          onChange={handleFileChange} 
          accept="image/*" 
          className="d-none" 
        />

        {/* Action Controls */}
        {!isCropping && (
          <Stack direction="horizontal" gap={2} className="justify-content-center">
            {!capturedImage ? (
              <>
                <Button 
                  className="btn-loob-primary flex-fill" 
                  onClick={handleCaptureClick}
                  disabled={!cameraActive || isAnalyzing}
                >
                  <span className="me-2">◉</span> CAPTURE
                </Button>
                <Button 
                  className="btn-loob-secondary flex-fill" 
                  onClick={() => fileInputRef.current && fileInputRef.current.click()}
                  disabled={isAnalyzing}
                >
                  <span className="me-2">↑</span> Upload Image
                </Button>
              </>
            ) : (
              <>
                <Button 
                  className="btn-loob-secondary py-2 px-3" 
                  onClick={() => setIsCropping(true)}
                  disabled={isAnalyzing}
                  title="Select and crop lubricant region"
                >
                  <span className="me-1">✂</span> Crop Image
                </Button>
                <Button 
                  className="btn-loob-secondary py-2 px-3" 
                  onClick={onRetake}
                  disabled={isAnalyzing}
                >
                  <span className="me-1">↻</span> RETAKE
                </Button>
                <Button 
                  className="btn-loob-primary flex-fill py-2" 
                  onClick={onAnalyze}
                  disabled={isAnalyzing}
                >
                  {isAnalyzing ? (
                    <>
                      <Spinner animation="border" size="sm" className="me-2" />
                      ANALYZING...
                    </>
                  ) : (
                    <>
                      <span className="me-2">⚡</span> ANALYZE IMAGE
                    </>
                  )}
                </Button>
              </>
            )}
          </Stack>
        )}
      </Card.Body>
    </Card>
  );
}

// ============================================================
// RESULT ANALYSIS & TECHNICAL DETAILS PANEL
// ============================================================
function ResultPanel({ result, isAnalyzing, error, onNewAnalysis, onRetry }) {
  const [reasoningTheme, setReasoningTheme] = useState('gold');

  if (isAnalyzing) {
    return (
      <Card className="loob-card h-100">
        <div className="loob-card-header">RESULT ANALYSIS</div>
        <Card.Body className="loading-box d-flex flex-column align-items-center justify-content-center">
          <Spinner animation="border" variant="info" style={{ width: '3.5rem', height: '3.5rem' }} className="mb-4" />
          <h5 className="fw-bold text-light mb-2">ANALYZING SAMPLE</h5>
          <p className="text-muted small">Please wait while the AI analysis pipeline evaluates the lubricant sample...</p>
          
          <div className="loading-steps">
            <div className="loading-step-item loading-step-active">
              <span className="pulse-dot"></span> Verifying lubricant sample
            </div>
            <div className="loading-step-item loading-step-active">
              <span className="pulse-dot"></span> Running AI visual analysis (EfficientNet-B3, Color, Texture)
            </div>
            <div className="loading-step-item loading-step-active">
              <span className="pulse-dot"></span> Combining weighted model evidence
            </div>
            <div className="loading-step-item loading-step-active">
              <span className="pulse-dot"></span> Generating final assessment
            </div>
          </div>
        </Card.Body>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="loob-card h-100">
        <div className="loob-card-header">RESULT ANALYSIS</div>
        <Card.Body className="p-4 text-center d-flex flex-column align-items-center justify-content-center">
          <Alert variant="danger" className="bg-transparent border-danger text-danger w-100 p-4 mb-4">
            <h5 className="fw-bold mb-2">ANALYSIS FAILED</h5>
            <p className="small mb-0">Unable to complete the lubricant analysis. Please try again.</p>
          </Alert>
          <Button className="btn-loob-primary px-4" onClick={onRetry}>
            ↻ RETRY
          </Button>
        </Card.Body>
      </Card>
    );
  }

  if (!result) {
    return (
      <Card className="loob-card h-100">
        <div className="loob-card-header">RESULT ANALYSIS</div>
        <Card.Body className="p-4 text-center d-flex flex-column align-items-center justify-content-center text-muted" style={{ minHeight: '350px' }}>
          <svg width="54" height="54" viewBox="0 0 24 24" fill="none" stroke="#2c3e66" strokeWidth="1.5" className="mb-3">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
            <line x1="16" y1="13" x2="8" y2="13"/>
            <line x1="16" y1="17" x2="8" y2="17"/>
          </svg>
          <h6 className="fw-semibold text-light mb-1">Awaiting Lubricant Sample</h6>
          <p className="small text-muted max-w-sm mb-0">
            Capture or upload a sample image on the left, then click <strong>ANALYZE IMAGE</strong> to execute condition analysis.
          </p>
        </Card.Body>
      </Card>
    );
  }

  // Handle Non-Lubricant Rejection Gate
  if (result.is_lubricant === false || result.final_class === "non-lubricant") {
    return (
      <Card className="loob-card h-100">
        <div className="loob-card-header text-warning">RESULT ANALYSIS</div>
        <Card.Body className="p-4">
          <div className="text-center p-4 border border-warning rounded-3 mb-4" style={{ background: 'rgba(245, 166, 35, 0.08)' }}>
            <Badge bg="warning" text="dark" className="px-3 py-2 fs-6 fw-bold mb-3">
              SAMPLE NOT IDENTIFIED
            </Badge>
            <h4 className="fw-bold text-light mb-2">NON-LUBRICANT IMAGE</h4>
            <p className="text-muted small mb-0">
              The submitted image was not identified as a suitable lubricant sample by the Vision Verification Gate.
            </p>
          </div>

          <div className="recommendation-card">
            <div className="recommendation-title">RECOMMENDATION</div>
            <p className="recommendation-text">
              Please capture a clear, well-lit image containing the lubricant sample inside the square ROI guide and try again.
            </p>
          </div>

          {result.gate_reasoning && (
            <Accordion className="loob-accordion mb-4">
              <Accordion.Item eventKey="0">
                <Accordion.Header>GATE REASONING</Accordion.Header>
                <Accordion.Body>
                  <div className="gate-reasoning-content">
                    {result.gate_reasoning}
                  </div>
                </Accordion.Body>
              </Accordion.Item>
            </Accordion>
          )}

          <Button className="btn-loob-primary w-100" onClick={onNewAnalysis}>
            ↻ TRY AGAIN
          </Button>
        </Card.Body>
      </Card>
    );
  }

  // Calculate / Parse Result Parameters
  let finalClass = (result.final_class || "").toLowerCase();
  let statusText = result.status || "";
  let confidenceVal = typeof result.confidence === "number" ? result.confidence : 0;

  // Fallback calculation if final_class was not set directly by LLM
  if (!finalClass || !["c1", "c2", "c3"].includes(finalClass)) {
    const ev = result.model_evidence || {};
    const effPred = (result.efficientnet_evidence?.prediction || ev.efficientnet?.prediction || "").toLowerCase();
    const colPred = (result.color_evidence?.prediction || ev.color?.prediction || "").toLowerCase();
    const texPred = (result.texture_evidence?.prediction || ev.texture?.prediction || "").toLowerCase();

    const counts = { c1: 0, c2: 0, c3: 0 };
    if (effPred in counts) counts[effPred] += 0.55;
    if (colPred in counts) counts[colPred] += 0.15;
    if (texPred in counts) counts[texPred] += 0.30;

    finalClass = Object.keys(counts).reduce((a, b) => counts[a] > counts[b] ? a : b);
    const statusMap = { c1: "Fresh", c2: "Semi-degraded", c3: "Fully-degraded" };
    statusText = statusMap[finalClass] || "Analyzed";
    confidenceVal = counts[finalClass] || 0.85;
  }

  // Apply Classification Safety Rule
  if ((finalClass === "c1" || finalClass === "c2") && confidenceVal < 0.55) {
    finalClass = "c3";
    statusText = "Fully-degraded";
  }

  const confidencePercentage = (confidenceVal * 100).toFixed(1) + "%";

  // Class Visual Styling Definitions
  const classConfigs = {
    c1: {
      cardClass: "condition-c1",
      badgeClass: "grade-badge-c1",
      grade: "C1",
      title: "INITIAL STAGE OF DEGRADATION",
      subtitle: "(HEALTHY)",
      recommendation: "The lubricant sample displays characteristics of fresh, healthy oil. Lubricant condition is optimal for continued operational use."
    },
    c2: {
      cardClass: "condition-c2",
      badgeClass: "grade-badge-c2",
      grade: "C2",
      title: "TRANSITIONAL DEGRADATION",
      subtitle: "(USABLE BUT GOING TO DEGRADE SOON)",
      recommendation: "The lubricant displays moderate degradation markers. Monitoring frequency should be increased, and schedule preventive maintenance replacement in the near term."
    },
    c3: {
      cardClass: "condition-c3",
      badgeClass: "grade-badge-c3",
      grade: "C3",
      title: "ADVANCED DEGRADATION",
      subtitle: "(AVOID USAGE)",
      recommendation: "The lubricant shows visual characteristics associated with advanced degradation. Avoid usage and consider immediate lubricant replacement."
    }
  };

  const currentConfig = classConfigs[finalClass] || classConfigs.c3;

  return (
    <Card className="loob-card h-100">
      <div className="loob-card-header">
        <span>RESULT ANALYSIS</span>
        <Button size="sm" className="btn-loob-secondary py-1 px-3" onClick={onNewAnalysis}>
          ↻ NEW ANALYSIS
        </Button>
      </div>

      <Card.Body className="p-4">
        {/* Large Condition Result Card */}
        <div className={`condition-card ${currentConfig.cardClass}`}>
          <div className="text-uppercase text-muted fw-bold mb-2" style={{ fontSize: '0.75rem', letterSpacing: '1px' }}>
            ANALYSIS RESULT
          </div>
          <div className={currentConfig.badgeClass}>
            {currentConfig.grade} GRADE DETECTED
          </div>
          <div className="condition-title">{currentConfig.title}</div>
          <div className="condition-subtitle">{currentConfig.subtitle}</div>
        </div>

        {/* Confidence Box */}
        <div className="confidence-box">
          <span className="confidence-label">System Confidence</span>
          <span className="confidence-value">{confidencePercentage}</span>
        </div>

        {/* Recommendation Card */}
        <div className="recommendation-card">
          <div className="recommendation-title">RECOMMENDATION</div>
          <p className="recommendation-text">{currentConfig.recommendation}</p>
        </div>

        {/* Accordions for Technical Evidence & Reports */}
        <Accordion defaultActiveKey="0" className="loob-accordion mb-3">
          
          {/* MODEL EVIDENCE ACCORDION */}
          <Accordion.Item eventKey="0">
            <Accordion.Header>▼ MODEL EVIDENCE</Accordion.Header>
            <Accordion.Body>
              <p className="small mb-3 text-secondary-light">
                Evidence extracted from the individual parallel machine-learning classifiers:
              </p>

              <Table responsive className="loob-table align-middle">
                <thead>
                  <tr>
                    <th>Model Component</th>
                    <th>Prediction</th>
                    <th>C1 %</th>
                    <th>C2 %</th>
                    <th>C3 %</th>
                  </tr>
                </thead>
                <tbody>
                  {renderModelEvidenceRow("EfficientNet-B3", result.efficientnet_evidence || result.model_evidence?.efficientnet)}
                  {renderModelEvidenceRow("Color Analysis", result.color_evidence || result.model_evidence?.color)}
                  {renderModelEvidenceRow("Texture Analysis", result.texture_evidence || result.model_evidence?.texture)}
                </tbody>
              </Table>

              {/* MODEL WEIGHTS (FIXED DISPLAY) */}
              <div className="weights-container">
                <div className="d-flex justify-content-between align-items-center mb-2">
                  <span className="fw-bold text-light small">FIXED MODEL WEIGHTS</span>
                  <Badge bg="dark" className="text-light border border-secondary font-monospace">READ-ONLY</Badge>
                </div>
                <div className="weight-row">
                  <span className="text-light">EfficientNet-B3</span>
                  <span className="fw-bold text-cyan-light">55%</span>
                </div>
                <div className="weight-row">
                  <span className="text-light">Color Analysis</span>
                  <span className="fw-bold text-cyan-light">15%</span>
                </div>
                <div className="weight-row">
                  <span className="text-light">Texture Analysis</span>
                  <span className="fw-bold text-cyan-light">30%</span>
                </div>
              </div>

              {/* MODEL AGREEMENT */}
              <div className="mt-3 d-flex align-items-center justify-content-between p-2 rounded" style={{ background: 'var(--loob-bg-secondary)' }}>
                <span className="small text-light fw-semibold">MODEL AGREEMENT</span>
                {renderAgreementBadge(result)}
              </div>
            </Accordion.Body>
          </Accordion.Item>

          {/* AI ANALYSIS REPORT ACCORDION */}
          {result.analysis_report && (
            <Accordion.Item eventKey="1">
              <Accordion.Header>▼ AI ANALYSIS REPORT</Accordion.Header>
              <Accordion.Body>
                <div className="analysis-report-content font-monospace small">
                  {result.analysis_report}
                </div>
              </Accordion.Body>
            </Accordion.Item>
          )}

          {/* DECISION REASONING ACCORDION */}
          {result.reasoning && (
            <Accordion.Item eventKey="2">
              <Accordion.Header>▼ DECISION REASONING</Accordion.Header>
              <Accordion.Body>
                <div className="d-flex align-items-center justify-content-between mb-2 pb-1 border-bottom border-secondary border-opacity-25">
                  <span className="small fw-bold text-uppercase" style={{ color: '#94a3b8', letterSpacing: '0.8px', fontSize: '0.72rem' }}>
                    AI Decision Narrative
                  </span>
                  <div className="d-flex align-items-center gap-1">
                    <span className="small me-1 text-muted" style={{ fontSize: '0.72rem' }}>Text Color:</span>
                    <button
                      type="button"
                      className={`btn btn-sm py-0 px-2 rounded-pill ${reasoningTheme === 'gold' ? 'btn-warning text-dark fw-bold' : 'btn-outline-secondary text-light'}`}
                      style={{ fontSize: '0.72rem' }}
                      onClick={(e) => { e.stopPropagation(); setReasoningTheme('gold'); }}
                      title="Amber Gold"
                    >
                      ● Amber Gold
                    </button>
                    <button
                      type="button"
                      className={`btn btn-sm py-0 px-2 rounded-pill ${reasoningTheme === 'cyan' ? 'btn-info text-dark fw-bold' : 'btn-outline-secondary text-light'}`}
                      style={{ fontSize: '0.72rem' }}
                      onClick={(e) => { e.stopPropagation(); setReasoningTheme('cyan'); }}
                      title="Sky Cyan"
                    >
                      ● Sky Cyan
                    </button>
                    <button
                      type="button"
                      className={`btn btn-sm py-0 px-2 rounded-pill ${reasoningTheme === 'mint' ? 'btn-success text-dark fw-bold' : 'btn-outline-secondary text-light'}`}
                      style={{ fontSize: '0.72rem' }}
                      onClick={(e) => { e.stopPropagation(); setReasoningTheme('mint'); }}
                      title="Mint Green"
                    >
                      ● Mint Green
                    </button>
                  </div>
                </div>
                <div 
                  className={`decision-reasoning-content decision-reasoning-${reasoningTheme}`}
                  style={{
                    color: reasoningTheme === 'cyan' ? '#38bdf8' : reasoningTheme === 'mint' ? '#4ade80' : '#fde047',
                    borderLeftColor: reasoningTheme === 'cyan' ? '#38bdf8' : reasoningTheme === 'mint' ? '#4ade80' : '#fde047',
                    fontWeight: 500
                  }}
                >
                  {result.reasoning}
                </div>
              </Accordion.Body>
            </Accordion.Item>
          )}

        </Accordion>
      </Card.Body>
    </Card>
  );
}

// Helper to render individual model evidence row
function renderModelEvidenceRow(name, data) {
  if (!data) {
    return (
      <tr>
        <td className="fw-semibold text-light">{name}</td>
        <td className="text-secondary-light">N/A</td>
        <td className="text-secondary-light">-</td>
        <td className="text-secondary-light">-</td>
        <td className="text-secondary-light">-</td>
      </tr>
    );
  }

  const pred = (data.prediction || "-").toUpperCase();
  const probs = data.probabilities || {};
  const formatProb = (v) => typeof v === "number" ? (v * 100).toFixed(1) + "%" : "0.0%";

  return (
    <tr>
      <td className="fw-semibold text-light">{name}</td>
      <td>
        <Badge bg={pred === "C1" ? "success" : pred === "C2" ? "warning" : "danger"} className="px-2 py-1">
          {pred}
        </Badge>
      </td>
      <td className="text-light fw-semibold">{formatProb(probs.c1)}</td>
      <td className="text-light fw-semibold">{formatProb(probs.c2)}</td>
      <td className="text-light fw-semibold">{formatProb(probs.c3)}</td>
    </tr>
  );
}

// Helper to render agreement badge
function renderAgreementBadge(result) {
  const agreement = result.model_evidence?.agreement;
  if (agreement && agreement.models_supporting === agreement.total_models) {
    return <Badge bg="success" className="px-2 py-1">✓ All models agree</Badge>;
  } else if (agreement) {
    return <Badge bg="warning" text="dark" className="px-2 py-1">⚠ Models show disagreement</Badge>;
  }
  return <Badge bg="success" className="px-2 py-1">✓ Models in agreement</Badge>;
}

// ============================================================
// MAIN APP COMPONENT
// ============================================================
function App() {
  const [selectedModel, setSelectedModel] = useState("Original Image Model");
  const [capturedImage, setCapturedImage] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [resultData, setResultData] = useState(null);
  const [errorState, setErrorState] = useState(null);

  const handleCapture = (imageData) => {
    setCapturedImage(imageData);
    setResultData(null);
    setErrorState(null);
  };

  const handleUpload = (imageData) => {
    setCapturedImage(imageData);
    setResultData(null);
    setErrorState(null);
  };

  const handleRetake = () => {
    setCapturedImage(null);
    setResultData(null);
    setErrorState(null);
  };

  const handleNewAnalysis = () => {
    setCapturedImage(null);
    setResultData(null);
    setErrorState(null);
  };

  const handleAnalyze = async () => {
    if (!capturedImage) return;

    setIsAnalyzing(true);
    setErrorState(null);

    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: capturedImage })
      });

      if (!response.ok) {
        throw new Error(`Server returned error status ${response.status}`);
      }

      const data = await response.json();
      console.log("[LOOB VISION] API Response:", data);
      setResultData(data);
    } catch (err) {
      console.error("[LOOB VISION] Analysis error:", err);
      setErrorState(err.message || "Failed to complete lubricant analysis");
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="d-flex flex-column min-vh-100">
      <Header 
        selectedModel={selectedModel}
        onModelChange={setSelectedModel}
      />

      <main className="flex-fill py-4">
        <Container fluid className="px-3 px-md-4">
          <Row className="g-4 align-items-stretch">
            {/* LEFT COLUMN: CAMERA / IMAGE PREVIEW */}
            <Col lg={6} xl={6}>
              <CameraPanel 
                capturedImage={capturedImage}
                onCapture={handleCapture}
                onUpload={handleUpload}
                onRetake={handleRetake}
                onAnalyze={handleAnalyze}
                isAnalyzing={isAnalyzing}
              />
            </Col>

            {/* RIGHT COLUMN: RESULT ANALYSIS */}
            <Col lg={6} xl={6}>
              <ResultPanel 
                result={resultData}
                isAnalyzing={isAnalyzing}
                error={errorState}
                onNewAnalysis={handleNewAnalysis}
                onRetry={handleAnalyze}
              />
            </Col>
          </Row>
        </Container>
      </main>

      <footer className="loob-footer text-center">
        <Container>
          <div className="fw-semibold mb-1" style={{ letterSpacing: '1px' }}>
            LOOBVISION Industrial AI
          </div>
          <div className="text-muted small">
            AI-Powered Lubricant Condition Analysis & Automated Visual Screening System
          </div>
        </Container>
      </footer>
    </div>
  );
}

// Render React App
const rootElement = document.getElementById('root');
const root = ReactDOM.createRoot(rootElement);
root.render(<App />);
