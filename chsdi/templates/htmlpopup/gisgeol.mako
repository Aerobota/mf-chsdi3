<%inherit file="base.mako"/>

<%def name="table_body(c,lang)">
<%
    import markupsafe

    c['stable_id'] = False
    sgd_nr = c['layerBodId'] + '.' + 'sgd_nr'

    def br(text):
        return text.replace('\n', markupsafe.Markup('<br />'))
%>
    <tr><td class="cell-left">${_('ch.swisstopo.geologie-gisgeol-flaechen-100to1000km2.sgd_nr')}</td><td>${c['attributes']['sgd_nr']}</td></tr>
    <tr><td class="cell-left">${_('ch.swisstopo.geologie-gisgeol-punkte.orig_id')}</td><td>${c['attributes']['orig_id']}</td></tr>
    <tr><td class="cell-left">${_('title')}</td><td>${c['attributes']['title'] | br}</td></tr>
    <tr><td class="cell-left">${_('author')}</td><td>${c['attributes']['author'] | br}</td></tr>
    <tr><td class="cell-left">${_('ch.swisstopo.geologie-gisgeol-punkte.report_structure')}</td><td>${c['attributes']['report_structure'] | br}</td></tr>
    <tr><td class="cell-left">${_('ch.swisstopo.geologie-gisgeol-punkte.aux_info')}</td><td>${c['attributes']['aux_info'] | br}</td></tr>
    <tr><td class="cell-left">${_('doccreation_date')}</td><td>${c['attributes']['doccreation']}</td></tr>
    <tr>
    % if c['attributes']['pdf_url']:
    <tr>
          <td class="cell-left">${_('pdf_url')}</td>
          <td>
            <a href="${c['attributes']['pdf_url']}" target="_blank" title="Download ${c['attributes']['sgd_nr']}.pdf - ${c['attributes']['pdf_size']}" target="_blank">
              ${c['attributes']['sgd_nr']}.pdf - ${c['attributes']['pdf_size']}
            </a>
            <br>
          </td>
    </tr>
    <tr><td class="cell-left">${_('gisgeol_auskunft')}</td>
          <td>
            <a href="mailto:geolinfo@swisstopo.ch?subject=Query InfoGeol no.: ${c['attributes']['sgd_nr']}" target="_blank">
              geolinfo@swisstopo.ch - InfoGeol no.: ${c['attributes']['sgd_nr']}
            </a>
          </td>
    </tr>
    % else:
          <td class="cell-left">${_('pdf_url')}</td>
          <td> -
          </td>
    </tr>

        % if (c['attributes']['copy_avail']) == 'free' and (c['attributes']['view_avail']) == 'free':
                <tr><td class="cell-left">${_('gisgeol_auskunft')}</td>
          <td>
            <a href="mailto:geolinfo@swisstopo.ch?subject=Query InfoGeol no.: ${c['attributes']['sgd_nr']}" target="_blank">
              geolinfo@swisstopo.ch - InfoGeol no.: ${c['attributes']['sgd_nr']}
            </a>
          </td>
    </tr>
        % else:
    <tr><td class="cell-left">${_('gisgeol_auskunft')}</td>
          <td class="cell-left">
            ${_('gisgeol_auskunft_info')}
          </td>
    </tr>
        % endif
    % endif
</%def>
