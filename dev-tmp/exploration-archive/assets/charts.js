(function() {
  var style = getComputedStyle(document.documentElement);
  var accent = style.getPropertyValue('--accent').trim() || '#2563eb';
  var accent2 = style.getPropertyValue('--accent2').trim() || '#7c3aed';
  var ink = style.getPropertyValue('--ink').trim() || '#1a1a1a';
  var muted = style.getPropertyValue('--muted').trim() || '#6b7280';
  var rule = style.getPropertyValue('--rule').trim() || '#e5e4e0';

  // --- Chart: 竞品雷达图 ---
  var radarChart = echarts.init(document.getElementById('chart-radar'), null, { renderer: 'svg' });

  var option = {
    animation: false,
    tooltip: {
      appendToBody: true,
      trigger: 'item'
    },
    legend: {
      data: ['Fibery', 'Coda', 'ClickUp', 'Monday.com', 'NocoBase'],
      bottom: 0,
      textStyle: {
        color: ink,
        fontFamily: '"PingFang SC","Noto Sans CJK SC","Microsoft YaHei",sans-serif',
        fontSize: 12
      }
    },
    radar: {
      center: ['50%', '52%'],
      radius: '65%',
      indicator: [
        { name: '角色差异化视图', max: 10 },
        { name: '条件字段', max: 10 },
        { name: '流转/流程', max: 10 },
        { name: '动态调度', max: 10 },
        { name: '信息结构灵活', max: 10 }
      ],
      axisName: {
        color: ink,
        fontFamily: '"PingFang SC","Noto Sans CJK SC","Microsoft YaHei",sans-serif',
        fontSize: 12
      },
      splitArea: {
        areaStyle: {
          color: ['rgba(37, 99, 235, 0.02)', 'rgba(37, 99, 235, 0.02)']
        }
      },
      splitLine: {
        lineStyle: {
          color: rule
        }
      },
      axisLine: {
        lineStyle: {
          color: rule
        }
      }
    },
    series: [{
      type: 'radar',
      data: [
        {
          name: 'Fibery',
          value: [8, 4, 7, 5, 9],
          symbol: 'circle',
          symbolSize: 6,
          lineStyle: { color: accent, width: 2 },
          areaStyle: { color: 'rgba(37, 99, 235, 0.08)' },
          itemStyle: { color: accent }
        },
        {
          name: 'Coda',
          value: [6, 5, 5, 4, 8],
          symbol: 'circle',
          symbolSize: 6,
          lineStyle: { color: accent2, width: 2 },
          areaStyle: { color: 'rgba(124, 58, 237, 0.08)' },
          itemStyle: { color: accent2 }
        },
        {
          name: 'ClickUp',
          value: [7, 3, 8, 6, 6],
          symbol: 'circle',
          symbolSize: 6,
          lineStyle: { color: '#059669', width: 2 },
          areaStyle: { color: 'rgba(5, 150, 105, 0.08)' },
          itemStyle: { color: '#059669' }
        },
        {
          name: 'Monday.com',
          value: [5, 3, 6, 5, 5],
          symbol: 'circle',
          symbolSize: 6,
          lineStyle: { color: '#f59e0b', width: 2 },
          areaStyle: { color: 'rgba(245, 158, 11, 0.08)' },
          itemStyle: { color: '#f59e0b' }
        },
        {
          name: 'NocoBase',
          value: [7, 2, 6, 3, 8],
          symbol: 'circle',
          symbolSize: 6,
          lineStyle: { color: '#ef4444', width: 2 },
          areaStyle: { color: 'rgba(239, 68, 68, 0.08)' },
          itemStyle: { color: '#ef4444' }
        }
      ]
    }]
  };

  radarChart.setOption(option);
  window.addEventListener('resize', function() { radarChart.resize(); });
})();