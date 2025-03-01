import { useEffect, useState } from "react";
import axios from "axios";
import { Bar, Pie } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement } from "chart.js";

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement);

function Dashboard() {
  const [sentimentData, setSentimentData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    axios.get("http://localhost:5012/api/sentiment")
      .then((response) => {
        setSentimentData(response.data);
        setLoading(false);
      })
      .catch((err) => {
        setError("Error fetching data");
        setLoading(false);
      });
  }, []);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>{error}</p>;

  // Ensure data exists before using it
  if (!sentimentData || !sentimentData.positive_count) {
    return <p>No sentiment data available</p>;
  }

  // Prepare Data for Charts
  const sentimentChartData = {
    labels: ["Positive", "Negative", "Neutral"],
    datasets: [
      {
        label: "Sentiments",
        data: [
          sentimentData.positive_count,
          sentimentData.negative_count,
          sentimentData.neutral_count,
        ],
        backgroundColor: ["#4CAF50", "#F44336", "#FFEB3B"], // Green, Red, Yellow
        borderColor: ["#388E3C", "#D32F2F", "#FBC02D"],
        borderWidth: 1,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: { display: true },
      title: { display: true, text: "Sentiment Distribution" },
    },
    scales: {
      y: { beginAtZero: true },
    },
  };

  return (
    <div className="dashboard">
      <h2>Sentiment Analysis Dashboard</h2>
      <h3>Keyword: {sentimentData.keyword}</h3>

      <div className="charts">
        <div className="bar-chart">
          <h4>Sentiment Distribution</h4>
          <Bar data={sentimentChartData} options={chartOptions} />
        </div>

        <div className="pie-chart">
          <h4>Sentiment Proportion</h4>
          <Pie data={sentimentChartData} />
        </div>
      </div>

      <div className="aspect-analysis">
        <h3>Aspect-Based Sentiment Analysis (ABSA)</h3>
        {sentimentData.aspect_sentiments.map((aspect, index) => (
          <div key={index} className="aspect">
            <p><strong>{aspect.word}:</strong> Positive: {aspect.positive}, Negative: {aspect.negative}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Dashboard;
