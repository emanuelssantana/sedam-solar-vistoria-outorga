/* =============================================================================
   AGROPRIME & ECOVALE • BACKEND APPS SCRIPT CRM/ERP GLOBAL SEDAM
   Compatível com o Web App oficial da SEDAM Outorga:
   https://script.google.com/macros/s/AKfycbxYTqIPYbl8YOMfB1bY1qGkbRZLhvpPIOh7-IcwjHCdNrqoVWZDE0WfC13oQ_ry7wB3/exec
   ============================================================================= */

var TOKEN = 'sedam-outorga-campo-2026';
var PASTA_RAIZ = 'SEDAM_VISTORIAS_OUTORGA';
var ABA_VISTORIAS = 'VISTORIAS';
var ABA_CRM = 'CRM_PRODUTORES';
var ABA_CAMPANHAS = 'CRM_CAMPANHAS_NUTRICAO';

function doGet(e) {
  var p = (e && e.parameter) || {};
  var acao = p.acao || p.action || 'status';

  if (acao === 'listar' || acao === 'status') {
    return ContentService.createTextOutput(JSON.stringify({
      status: 'OK',
      versao: '3.0-CRM-ERP-IDS-FIXOS-CAMPANHAS',
      projeto: 'gen-lang-client-0913740404',
      regiao: 'southamerica-east1',
      dataset: 'sedam_analytics',
      timestamp: new Date().toISOString()
    })).setMimeType(ContentService.MimeType.JSON);
  }

  if (acao === 'listar_produtores' || acao === 'listar_crm') {
    return ContentService.createTextOutput(JSON.stringify(obterProdutoresSalvos()))
      .setMimeType(ContentService.MimeType.JSON);
  }

  if (acao === 'listar_campanhas') {
    return ContentService.createTextOutput(JSON.stringify(obterCampanhasNutricao()))
      .setMimeType(ContentService.MimeType.JSON);
  }

  return ContentService.createTextOutput(JSON.stringify({ erro: 'Ação GET desconhecida' }))
    .setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  try {
    var contents = (e && e.postData && e.postData.contents) ? e.postData.contents : '{}';
    var corpo = JSON.parse(contents);
    var acao = corpo.acao || corpo.action || 'vistoria';

    if (acao === 'salvar_produtor' || acao === 'salvar_crm') {
      var prod = corpo.produtor || corpo.dados || {};
      var res = salvarProdutorPlanilhaEDrive(prod);
      return ContentService.createTextOutput(JSON.stringify({
        status: res.status,
        mensagem: res.status === 'SUCESSO' ? 'Produtor salvo no Drive e Planilha.' : 'Gravação incompleta. Preserve a cópia local e tente novamente.',
        destinos: res.destinos,
        id_catalogo: res.id_catalogo,
        timestamp: new Date().toISOString()
      })).setMimeType(ContentService.MimeType.JSON);
    }

    if (acao === 'salvar_campanha_nutricao') {
      var itemCamp = corpo.campanha || corpo.interacao || corpo;
      var resCamp = salvarCampanhaNutricaoAntiColisao(itemCamp);
      return ContentService.createTextOutput(JSON.stringify(resCamp))
        .setMimeType(ContentService.MimeType.JSON);
    }

    if (acao === 'salvar_nota') {
      return ContentService.createTextOutput(JSON.stringify({
        status: 'NAO_IMPLEMENTADO',
        mensagem: 'Este backend não persiste notas. Preserve a cópia local.',
        id_catalogo: corpo.id_catalogo
      })).setMimeType(ContentService.MimeType.JSON);
    }

    // Compatibilidade com vistorias da Ficha V4
    return ContentService.createTextOutput(JSON.stringify({
      status: 'NAO_IMPLEMENTADO',
      mensagem: 'Esta ação não é persistida por este backend.',
      recebido: acao
    })).setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({
      status: 'ERRO',
      mensagem: String(err)
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

function obterProdutoresSalvos() {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    if (!ss) return { produtores: [] };
    var sh = ss.getSheetByName(ABA_CRM);
    if (!sh) return { produtores: [] };
    var dados = sh.getDataRange().getValues();
    if (dados.length <= 1) return { produtores: [] };
    var headers = dados[0];
    var lista = [];
    for (var i = 1; i < dados.length; i++) {
      var row = dados[i];
      var item = {};
      for (var j = 0; j < headers.length; j++) {
        item[headers[j]] = row[j];
      }
      lista.push(item);
    }
    return { status: 'OK', total: lista.length, produtores: lista };
  } catch (e) {
    return { status: 'ERRO', mensagem: String(e), produtores: [] };
  }
}

function salvarProdutorPlanilhaEDrive(prod) {
  var id = prod.id_catalogo || ('CLI-RO-' + Utilities.getUuid());
  prod.id_catalogo = id;
  prod.atualizado_em = new Date().toISOString();

  var destinos = { planilha: false, drive: false };
  var lock = LockService.getScriptLock();
  if (!lock.tryLock(10000)) return {id_catalogo: id, status: 'OCUPADO', destinos: destinos};
  try {
  // 1. Salva/Atualiza na Planilha
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    if (!ss) throw new Error('Planilha não configurada');
    if (ss) {
      var TARGET_COLS_17 = [
        'ID_CATALOGO', 'NOME_PRODUTOR', 'CPF_CNPJ', 'TIPO_PESSOA', 'MUNICIPIO',
        'ENDERECO_GLEBA', 'CONTATO_FURTADO', 'TELEFONES_INICIAIS', 'PROCESSO_NUP_SEI', 'PROCESSO_ANTIGO_SEDAM',
        'ATIVIDADE_PRINCIPAL', 'RESPONSAVEL_TECNICO', 'HISTORICO_CONTATOS',
        'GASTO_ESTIMADO_BRL', 'TAGS_SERVICOS', 'NOTAS_INTERNAS', 'ATUALIZADO_EM'
      ];
      var sh = ss.getSheetByName(ABA_CRM);
      if (!sh) {
        sh = ss.insertSheet(ABA_CRM);
        sh.appendRow(TARGET_COLS_17);
        sh.getRange(1, 1, 1, TARGET_COLS_17.length).setBackground('#064e3b').setFontColor('#ffffff').setFontWeight('bold');
      }

      var dados = sh.getDataRange().getValues();
      var header = dados.length > 0 ? dados[0].slice() : [];
      var linhaExistente = -1;
      for (var r = 1; r < dados.length; r++) {
        if (dados[r][0] === id) {
          linhaExistente = r + 1;
          break;
        }
      }

      var telsStr = Array.isArray(prod.telefones) ? prod.telefones.join('; ') : (prod.telefones || '');
      var seiList = Array.isArray(prod.processos_sei_nup) && prod.processos_sei_nup.length
        ? prod.processos_sei_nup
        : (Array.isArray(prod.processos_sei_lista) ? prod.processos_sei_lista : null);
      var seiStr = seiList ? seiList.join('; ') : (prod.processo_nup_sei || '');
      var antigoStr = Array.isArray(prod.processos_antigos_sedam) ? prod.processos_antigos_sedam.join('; ') : (prod.processo_antigo_sedam || '');
      var histStr = Array.isArray(prod.historico_contatos_documentais) ? JSON.stringify(prod.historico_contatos_documentais) : (prod.historico_contatos_documentais || '');

      var rowByHeader = {
        'ID_CATALOGO': id,
        'NOME_PRODUTOR': prod.nome_produtor_ou_empresa || '',
        'CPF_CNPJ': prod.cpf_cnpj || '',
        'TIPO_PESSOA': prod.tipo_pessoa || '',
        'MUNICIPIO': prod.municipio || 'Alta Floresta D\'Oeste',
        'ENDERECO_GLEBA': prod.endereco || prod.propriedade || '',
        'CONTATO_FURTADO': prod.contato_produtor_anotacao_furtado || '',
        'TELEFONES_INICIAIS': telsStr,
        'TELEFONES': telsStr,
        'PROCESSO_NUP_SEI': seiStr,
        'PROCESSO_ANTIGO_SEDAM': antigoStr,
        'ATIVIDADE_PRINCIPAL': prod.atividade_principal || '',
        'RESPONSAVEL_TECNICO': Array.isArray(prod.tecnicos) ? prod.tecnicos.join('; ') : (prod.tecnicos || ''),
        'HISTORICO_CONTATOS': histStr,
        'GASTO_ESTIMADO_BRL': prod.gasto_estimado_consultoria_brl || 0,
        'TAGS_SERVICOS': Array.isArray(prod.tags_servicos) ? prod.tags_servicos.join('; ') : (prod.tags_servicos || ''),
        'NOTAS_INTERNAS': prod.notas_internas || '',
        'IMOVEL_ID_FIXO': (prod.id_fixo_global && prod.id_fixo_global.imovel_id_fixo) || prod.imovel_id_fixo || '',
        'PLACA_SOLAR_STATUS': prod.placa_solar_status || (prod.diagnostico_perfil && prod.diagnostico_perfil.placa_solar_status) || '',
        'BOMBA_INFO': prod.bomba_info || (prod.diagnostico_perfil && prod.diagnostico_perfil.bomba_info) || '',
        'MOTIVO_CAMPANHA': prod.motivo_campanha || '',
        'ATUALIZADO_EM': prod.atualizado_em
      };

      var activeHeaders = TARGET_COLS_17;
      if (header.length >= 13) {
        var extraCols = ['CONTATO_FURTADO', 'PROCESSO_NUP_SEI', 'PROCESSO_ANTIGO_SEDAM', 'HISTORICO_CONTATOS']
          .filter(function(col) { return header.indexOf(col) === -1; });
        if (extraCols.length > 0) {
          var hdrRange = sh.getRange(1, header.length + 1, 1, extraCols.length);
          hdrRange.setValues([extraCols]);
          hdrRange.setBackground('#064e3b').setFontColor('#ffffff').setFontWeight('bold');
          header = header.concat(extraCols);
        }
        activeHeaders = header;
      }

      var rowValues = activeHeaders.map(function(col) {
        return Object.prototype.hasOwnProperty.call(rowByHeader, col) ? rowByHeader[col] : '';
      });

      rowValues = rowValues.map(function(value) { return typeof value === 'string' && /^[=+@-]/.test(value) ? "'" + value : value; });
      if (linhaExistente > 0) {
        sh.getRange(linhaExistente, 1, 1, rowValues.length).setValues([rowValues]);
      } else {
        sh.appendRow(rowValues);
      }
      SpreadsheetApp.flush();
      destinos.planilha = true;
    }
  } catch (errPlanilha) {
    Logger.log('Erro ao salvar na planilha CRM: ' + errPlanilha);
  }

  // 2. Salva arquivo JSON na pasta do Drive
  try {
    var pastas = DriveApp.getFoldersByName(PASTA_RAIZ);
    var pastaRaiz = pastas.hasNext() ? pastas.next() : DriveApp.createFolder(PASTA_RAIZ);
    var subpastas = pastaRaiz.getFoldersByName('CRM_CADASTROS');
    var pastaCrm = subpastas.hasNext() ? subpastas.next() : pastaRaiz.createFolder('CRM_CADASTROS');

    var nomeArquivo = id + '_' + (prod.nome_produtor_ou_empresa || 'PRODUTOR').replace(/[^a-zA-Z0-9]/g, '_') + '.json';
    var arquivos = pastaCrm.getFilesByName(nomeArquivo);
    if (arquivos.hasNext()) {
      arquivos.next().setContent(JSON.stringify(prod, null, 2));
    } else {
      pastaCrm.createFile(nomeArquivo, JSON.stringify(prod, null, 2), MimeType.PLAIN_TEXT);
    }
    destinos.drive = true;
  } catch (errDrive) {
    Logger.log('Erro ao salvar JSON no Drive: ' + errDrive);
  }

  return { id_catalogo: id, status: destinos.planilha && destinos.drive ? 'SUCESSO' : (destinos.planilha || destinos.drive ? 'PARCIAL' : 'ERRO'), destinos: destinos };
  } finally { lock.releaseLock(); }
}

function obterCampanhasNutricao() {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    if (!ss) return { status: 'OK', campanhas: [] };
    var sh = ss.getSheetByName(ABA_CAMPANHAS);
    if (!sh) return { status: 'OK', campanhas: [] };
    var dados = sh.getDataRange().getValues();
    if (dados.length <= 1) return { status: 'OK', campanhas: [] };
    var headers = dados[0];
    var lista = [];
    for (var i = 1; i < dados.length; i++) {
      var obj = {};
      for (var j = 0; j < headers.length; j++) obj[headers[j]] = dados[i][j];
      lista.push(obj);
    }
    return { status: 'OK', total: lista.length, campanhas: lista };
  } catch (e) {
    return { status: 'ERRO', mensagem: String(e), campanhas: [] };
  }
}

function salvarCampanhaNutricaoAntiColisao(camp) {
  var c = camp || {};
  var cliId = String(c.cliente_id_fixo || c.id_catalogo || '').trim();
  var solId = String(c.solucao_id_fixo || '').trim();
  var trilhaId = String(c.trilha_id_fixo || 'TRL-GERAL').trim();
  var campId = String(c.campanha_id_fixo || 'CAMP-MANUAL').trim();
  var janela = String(c.janela_yyyymm || new Date().toISOString().slice(0, 7).replace('-', '')).trim();
  var canal = String(c.canal || 'WHATSAPP_CRM').trim();
  var key = String(c.idempotency_key || (cliId + '|' + solId + '|' + trilhaId + '|' + campId + '|' + janela + '|' + canal)).toUpperCase();

  if (!cliId || !solId) {
    return { status: 'ERRO', mensagem: 'cliente_id_fixo e solucao_id_fixo são obrigatórios.', idempotency_key: key };
  }

  var lock = LockService.getScriptLock();
  if (!lock.tryLock(10000)) {
    return { status: 'OCUPADO', colisao_evitada: true, idempotency_key: key };
  }
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    if (!ss) throw new Error('Planilha não configurada');
    var COLS = [
      'IDEMPOTENCY_KEY', 'REGISTRO_ID', 'CLIENTE_ID_FIXO', 'IMOVEL_ID_FIXO',
      'NOME_PRODUTOR', 'TECNICO_ID_FIXO', 'TRILHA_ID_FIXO', 'SOLUCAO_ID_FIXO',
      'CAMPANHA_ID_FIXO', 'JANELA_YYYYMM', 'CANAL', 'STATUS_ENVIO',
      'RESUMO_PERSONALIZADO', 'ATUALIZADO_EM'
    ];
    var sh = ss.getSheetByName(ABA_CAMPANHAS);
    if (!sh) {
      sh = ss.insertSheet(ABA_CAMPANHAS);
      sh.appendRow(COLS);
      sh.getRange(1, 1, 1, COLS.length).setBackground('#1e3a8a').setFontColor('#ffffff').setFontWeight('bold');
    }
    var dados = sh.getDataRange().getValues();
    for (var r = 1; r < dados.length; r++) {
      if (String(dados[r][0]).trim().toUpperCase() === key) {
        return {
          status: 'COLISAO_BLOQUEADA_IDEMPOTENTE',
          colisao_evitada: true,
          idempotency_key: key,
          mensagem: 'Interação já registrada para esta trilha/janela; disparo duplicado bloqueado.',
          destinos: { planilha: true }
        };
      }
    }
    var nowIso = new Date().toISOString();
    var regId = String(c.registro_id || ('NUT-' + Utilities.getUuid()));
    var row = [
      key,
      regId,
      cliId,
      String(c.imovel_id_fixo || ''),
      String(c.nome_produtor || ''),
      String(c.tecnico_id_fixo || ''),
      trilhaId,
      solId,
      campId,
      janela,
      canal,
      String(c.status_envio || 'AGENDADO_CRM'),
      String(c.resumo_personalizado || ''),
      nowIso
    ].map(function(value) { return typeof value === 'string' && /^[=+@-]/.test(value) ? "'" + value : value; });
    sh.appendRow(row);
    SpreadsheetApp.flush();
    return {
      status: 'SUCESSO',
      colisao_evitada: false,
      idempotency_key: key,
      registro_id: regId,
      destinos: { planilha: true },
      timestamp: nowIso
    };
  } catch (err) {
    return { status: 'ERRO', mensagem: String(err), idempotency_key: key };
  } finally {
    lock.releaseLock();
  }
}
