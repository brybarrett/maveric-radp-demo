import React, { useState } from 'react';
import ProgressTracker from './ProgressTracker';
import './GuidedTour.css';

function GuidedTour({ onSendMessage, onExitTour }) {
  const [currentStage, setCurrentStage] = useState(0);
  const [tourStarted, setTourStarted] = useState(false);

  const stages = [
    {
      name: 'Overview',
      title: 'What is Maveric RADP?',
      content: `Maveric RADP is a comprehensive platform for simulating and optimizing Radio Access Networks (RAN). It helps network engineers and researchers understand network behavior, predict performance, and optimize configurations without expensive physical testing.

**The Platform Workflow**

Maveric RADP works through four connected stages, each building on the previous one. Think of it as a pipeline that transforms network configurations into actionable insights.

**What You'll Learn in This Tour**

By the end of this guided tour, you'll understand:
- How the platform processes network simulations from start to finish
- The role each component plays in the workflow
- How to leverage the platform for your specific use cases

Let's walk through each stage together.`,
      deepDivePrompt: 'Explain the key benefits and use cases of Maveric RADP in detail',
      continuePrompt: 'Continue to Setup'
    },
    {
      name: 'Setup',
      title: 'Stage 1: Simulation Configuration',
      content: `Every simulation starts with defining what you want to test. This is where you configure your network environment, set parameters, and define the scenario you want to analyze.

**What Happens in Setup**

You define the network topology - the physical layout of cells, sectors, and coverage areas. You also set simulation parameters like frequency bands, power levels, and the characteristics of user equipment (UEs) in the network.

**Think of It Like This**

Setup is like creating a blueprint. You're telling the platform: "Here's my network layout, here are my constraints, and here's what I want to simulate." The platform takes these inputs and prepares them for processing.

**Key Configuration Areas**
- Network topology and cell layouts
- Radio frequency parameters
- User equipment distribution and behavior
- Simulation duration and resolution

Once your configuration is complete, the platform moves to the intelligent prediction phase.`,
      deepDivePrompt: 'Show me detailed examples of network topology configuration and simulation parameters',
      continuePrompt: 'Continue to Digital Twin'
    },
    {
      name: 'Digital Twin',
      title: 'Stage 2: Digital Twin Intelligence',
      content: `This is where machine learning enters the picture. The Digital Twin creates an intelligent model that learns from data to predict network behavior rapidly and accurately.

**Why Digital Twin Matters**

Traditional RF simulations can take hours or days to run. The Digital Twin learns patterns from historical data and can predict outcomes in seconds. It's like having an expert network engineer who's seen thousands of scenarios and can instantly tell you what will happen.

**How It Works**

The platform trains machine learning models on network data, learning the complex relationships between configuration parameters and performance outcomes. Once trained, this Digital Twin can make predictions almost instantly.

**What Gets Predicted**
- Signal strength and quality across the coverage area
- Interference patterns between cells
- Network capacity and throughput
- User experience metrics

With the Digital Twin trained, we can now predict RF performance for any scenario.`,
      deepDivePrompt: 'Explain how the Digital Twin training process works and what algorithms are used',
      continuePrompt: 'Continue to RF Prediction'
    },
    {
      name: 'RF Prediction',
      title: 'Stage 3: RF Performance Analysis',
      content: `Now the trained Digital Twin model is put to work. The RF Prediction stage takes your configuration and generates detailed predictions about radio frequency performance across your network.

**What Gets Analyzed**

The platform predicts key performance indicators like signal strength (RSRP), signal quality (RSRQ), and signal-to-noise ratios (SINR) for every point in your coverage area. It identifies potential issues like coverage gaps, interference hotspots, and capacity constraints.

**Understanding the Output**

You receive comprehensive performance metrics that show exactly how your network will behave. This includes coverage maps, interference analysis, and throughput predictions - all generated in a fraction of the time traditional simulations would take.

**Real Value**

Instead of "configure, simulate, wait, analyze, repeat," you can test multiple scenarios quickly. Want to see how adding a new cell affects performance? Get the answer in seconds, not hours.

Finally, the platform orchestrates all these components working together.`,
      deepDivePrompt: 'Show me examples of RF prediction outputs and how to interpret coverage maps',
      continuePrompt: 'Continue to Orchestration'
    },
    {
      name: 'Orchestration',
      title: 'Stage 4: Workflow Orchestration',
      content: `The Orchestration layer is the conductor of the symphony. It manages the entire workflow, coordinates distributed processing, and ensures everything runs smoothly at scale.

**Behind the Scenes**

When you run complex simulations, the platform distributes work across multiple processing nodes, manages job queues, collects results, and handles any failures gracefully. You don't see this complexity - you just get fast, reliable results.

**Why This Matters**

Orchestration enables the platform to handle:
- Large-scale simulations across extensive networks
- Multiple concurrent jobs from different users
- Automatic recovery from processing failures
- Efficient resource utilization

**The Complete Picture**

Now you understand the full workflow: Configure your scenario (Setup), train intelligent models (Digital Twin), generate predictions (RF Analysis), and scale it all reliably (Orchestration).

**Ready to Explore?**

You now have the foundation. From here, you can dive deep into any component, ask specific questions, or explore use cases relevant to your work.`,
      deepDivePrompt: 'Explain the orchestration architecture and how distributed processing works',
      continuePrompt: 'Complete Tour'
    }
  ];

  const handleStartTour = () => {
    setTourStarted(true);
  };

  const handleContinue = () => {
    if (currentStage < stages.length - 1) {
      setCurrentStage(currentStage + 1);
    } else {
      // Tour complete
      onExitTour();
    }
  };

  const handleDeepDive = () => {
    onSendMessage(stages[currentStage].deepDivePrompt);
  };

  const handleAskQuestion = () => {
    onExitTour();
  };

  const handleStageClick = (index) => {
    if (index <= currentStage || index === currentStage + 1) {
      setCurrentStage(index);
    }
  };

  if (!tourStarted) {
    return (
      <div className="tour-welcome">
        <div className="tour-welcome-content">
          <h2>Welcome to Maveric RADP Documentation</h2>
          <p>
            I can guide you through the platform step-by-step, or answer specific questions about any component.
          </p>
          <div className="tour-welcome-options">
            <button className="tour-btn tour-btn-primary" onClick={handleStartTour}>
              Start Guided Tour
            </button>
            <button className="tour-btn tour-btn-secondary" onClick={handleAskQuestion}>
              Ask a Question
            </button>
          </div>
        </div>
      </div>
    );
  }

  const stage = stages[currentStage];

  return (
    <div className="guided-tour">
      <ProgressTracker 
        currentStage={currentStage} 
        stages={stages}
        onStageClick={handleStageClick}
      />
      
      <div className="tour-stage-content">
        <div className="tour-stage-header">
          <div className="tour-stage-number">Stage {currentStage + 1} of {stages.length}</div>
          <h2 className="tour-stage-title">{stage.title}</h2>
        </div>
        
        <div className="tour-stage-body">
          {stage.content.split('\n\n').map((paragraph, idx) => {
            if (paragraph.startsWith('**') && paragraph.endsWith('**')) {
              return (
                <h3 key={idx} className="tour-section-title">
                  {paragraph.replace(/\*\*/g, '')}
                </h3>
              );
            }
            
            if (paragraph.startsWith('- ')) {
              const items = paragraph.split('\n').filter(line => line.trim());
              return (
                <ul key={idx} className="tour-list">
                  {items.map((item, itemIdx) => (
                    <li key={itemIdx}>{item.replace(/^[-\d.]\s*/, '')}</li>
                  ))}
                </ul>
              );
            }
            
            return <p key={idx} className="tour-paragraph">{paragraph}</p>;
          })}
        </div>
        
        <div className="tour-stage-actions">
          <button className="tour-action-btn primary" onClick={handleContinue}>
            {currentStage < stages.length - 1 ? stage.continuePrompt : 'Start Exploring'}
          </button>
          <button className="tour-action-btn secondary" onClick={handleDeepDive}>
            Deep Dive: {stage.name}
          </button>
          <button className="tour-action-btn tertiary" onClick={handleAskQuestion}>
            Ask a Question
          </button>
        </div>
      </div>
    </div>
  );
}

export default GuidedTour;